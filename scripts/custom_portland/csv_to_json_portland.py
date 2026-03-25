"""
Module for converting CSV translation files to JSONL format.

This module processes CSV files containing translations in multiple languages
and converts them to JSONL (JSON Lines) format for the TranslationsDataset project.
It handles language code mapping, validates required columns, and generates structured
records with source text and translations.

Functions:
    find_language_code(column_name, lang_map): Matches a CSV column name to a language code
        with support for exact matches, case-insensitive matching, and language-specific quirks.
    convert_csv_to_jsonl(csv_path, lang_map): Converts a CSV file to JSONL format,
        creating records with English source text and translations in other languages.
        Returns the path to the processed output directory.
    main(): Entry point that processes all CSV files in the Portland data directory,
        converts them to JSONL, and generates data profile reports.

The module expects CSV files with an 'English' column (case-insensitive) and uses
the language_codes mapping from the data package to identify language columns.
Records are skipped if they contain only the source language without translations.
Output JSONL files are written in compact format to a processed/ directory structure.
"""

import json
import pandas as pd
from pathlib import Path
import sys

# Ensure the project root is on sys.path so the `data` package can be imported
# when this script is executed directly from the `scripts/` directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from data.language_codes import language_codes

def find_language_code(column_name, lang_map):
    # Check for exact match first
    if column_name in lang_map:
        return lang_map[column_name]["iso639-1"] or lang_map[column_name]["iso639-2"]
    
    # Check for case-insensitive match
    for lang, codes in lang_map.items():
        if lang.lower() == column_name.lower():
            return codes["iso639-1"] or codes["iso639-2"]
    
    # Handle specific quirks in the data
    if column_name.lower().startswith("farsi") or column_name.lower().startswith("persian"):
        return lang_map["Persian"]["iso639-1"] or lang_map["Persian"]["iso639-2"]
    elif column_name.lower().startswith("karen"):
        return lang_map["Karen"]["iso639-1"] or lang_map["Karen"]["iso639-2"]
    elif column_name.lower().startswith("trasitional chinese") or column_name.lower().startswith("traditional chinese"):
        return lang_map["Traditional Chinese"]["iso639-1"] or lang_map["Traditional Chinese"]["iso639-2"]
    
    print(f"Warning: Unrecognized language column '{column_name}' in CSV. Skipping this column.")
    return None

def convert_csv_to_jsonl(csv_path, lang_map=language_codes):

    df = pd.read_csv(csv_path)

    # make "English" check case-insensitive and normalize the column name to 'English'
    cols_lower = {c.lower(): c for c in df.columns}
    if "english" not in cols_lower:
        raise ValueError("CSV file must contain an 'English' column (case-insensitive).")
    actual_english = cols_lower["english"]
    if actual_english != "English":
        df = df.rename(columns={actual_english: "English"})
    
    # get the filepath, filename, and scenario name
    p = Path(csv_path)
    parent_filepath = p.parent
    scenario = p.stem.split("_", 1)[1]
    origin = p.stem.split("_", 1)[0]
    basename = p.stem
    json_filename = f"{basename}.jsonl"
    processed_filepath = parent_filepath.parent.parent / f"processed/{origin}"
    processed_filepath.mkdir(parents=True, exist_ok=True)
    jsonl_path = processed_filepath / json_filename

    records = []
    for i, row in df.iterrows():

        source_text = row["English"]

        translations = {}
        for col, val in row.items():
            if pd.isna(val):
                continue
            lang_code = find_language_code(col, lang_map)
            if lang_code:
                translations[lang_code] = str(val)
            else:
                print(f"Warning: Unrecognized language column '{col}' in CSV. Skipping this column.")
                continue

        # if length of translations is 1, skip this record since it doesn't have any translations
        if len(translations) <= 1:
            #print(f"Warning: Record {i} has only one translation (English). Skipping this record.")
            continue
        record = {
            "id": f"{origin}-{scenario}-{i:03d}",
            "scenario": scenario,
            "source": {"eng": source_text},
            "translations": translations
        }

        records.append(record)

    # use compact jsonl format
    with open(jsonl_path, "w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✓ Wrote {len(df)} records to {jsonl_path}")
    return processed_filepath

def main():
    # this is just for Portland data, select one file to set up the path
    csv_file = "data/raw/portland/portland_911_outage.csv"
    # make sure csv_file is a proper file path
    if not Path(csv_file).is_file():
        raise ValueError(f"CSV file {csv_file} does not exist.")
    
    # go through all of the *.csv files in the translationsdataset/data/raw/ directory
    for csv_path in Path(csv_file).parent.glob("*.csv"):
        csv_file = str(csv_path)
        print(f"Processing {csv_file}...")

        processed_filepath = convert_csv_to_jsonl(Path(csv_file), lang_map=language_codes)

    # then run the scripts/profile_of_data.py script to get the data profile for the Portland data
    from scripts.profile_of_translations import profile_translations
    profile_translations(processed_filepath)
    import scripts.profile_of_data
    scripts.profile_of_data.main(processed_filepath=processed_filepath)
    # import scripts.domain_counts_csv_to_latex
    # scripts.domain_counts_csv_to_latex.make_beautiful_files()

if __name__ == "__main__":
    main()
