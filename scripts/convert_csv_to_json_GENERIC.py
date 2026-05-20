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
import re
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
        # print(f"Exact match found: Column name '{column_name}' matches language '{column_name}'.")
        return  lang_map[column_name].get("BCP-47") or lang_map[column_name]["iso639-1"] or lang_map[column_name]["iso639-2"]
    
    # Check for case-insensitive match
    for lang, codes in lang_map.items():
        if lang.lower() == column_name.lower():
            return codes["BCP-47"] or codes["iso639-1"] or codes["iso639-2"]
    
    # Handle specific quirks in the data
    if column_name.lower().startswith("farsi") or column_name.lower().startswith("persian"):
        # print(f"Warning: Column name '{column_name}' is recognized as Persian/Farsi. Using ISO 639-1 code if available.")
        return lang_map["Persian"]["iso639-1"] or lang_map["Persian"]["iso639-2"]
    elif column_name.lower().startswith("karen"):
        # print(f"Warning: Column name '{column_name}' is recognized as Karen. Using ISO 639-1 code if available.")
        return lang_map["Karen"]["iso639-1"] or lang_map["Karen"]["iso639-2"]
    elif column_name.lower().startswith("trasitional chinese") or "traditional chinese" in column_name.lower():
        # print (f"Warning: Column name '{column_name}' is recognized as Traditional Chinese. Using BCP-47 code if available.")
        return lang_map["Traditional Chinese"]["BCP-47"] or lang_map["Traditional Chinese"]["iso639-1"] or lang_map["Traditional Chinese"]["iso639-2"]
    elif "simplified chinese" in column_name.lower():
        print (f"Warning: Column name '{column_name}' is recognized as Simplified Chinese. Using BCP-47 code if available.")
        return lang_map["Simplified Chinese"]["BCP-47"] or lang_map["Simplified Chinese"]["iso639-1"] or lang_map["Simplified Chinese"]["iso639-2"]


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
        if basename.lower().startswith("kc"):
            _, source_text_value = custom_kc_cleanup("English", source_text)  # apply custom cleanup to source text as well
        else:
            source_text_value = source_text

        translations = {}
        for col, val in row.items():
            if pd.isna(val):
                continue

            #### Custom cleanup handling for KC data ####
            col, val = custom_kc_cleanup(col, val)
            #### End of custom handling for KC data ####

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
            "source": {"eng": source_text_value},
            "translations": translations
        }

        records.append(record)

    # use compact jsonl format
    with open(jsonl_path, "w", encoding="utf-8") as out:
        for record in records:
            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✓ Wrote {len(df)} records to {jsonl_path}")
    return processed_filepath

def custom_kc_cleanup(col, val):
    if isinstance(val, str):
        val = val.replace("•\xa0\xa0\xa0\xa0\xa0", "").strip()
        val = re.sub(r"•\s+", "", val).strip()
        val = re.sub(r"·\s+", "", val).strip()
        if isinstance(val, str) and re.match(r"^\s*\d{1,2}\.", val):
            val = re.sub(r"^\s*\d{1,2}\.\s*", "", val).strip()
                # if val changed, print a warning
                # if val != row[col]:
                #     print(f"Warning: Cleaned value in column '{col}' for record {i} from '{row[col]}' to '{val}'.")
    if col.endswith(")") and "(" in col:
        col = col[:col.rfind("(")].strip()
    if col.lower() == "laotian":
        col = "lao"
    return col,val

def main():
    # Read folder path at runtime: first CLI arg, otherwise prompt
    if len(sys.argv) > 1:
        csv_dir = Path(sys.argv[1])
    else:
        csv_dir = Path(input("Enter folder path containing CSV files: ").strip())

    if not csv_dir.is_dir():
        raise ValueError(f"Folder {csv_dir} does not exist or is not a directory.")

    csv_files = sorted(csv_dir.glob("*.csv"))
    if not csv_files:
        raise ValueError(f"No CSV files found in {csv_dir}.")

    processed_filepath = None
    for csv_path in csv_files:
        print(f"Processing {csv_path}...")
        processed_filepath = convert_csv_to_jsonl(csv_path, lang_map=language_codes)

    # then run the scripts/profile_of_data.py script to get the data profile for the Portland data

    from scripts.profile_of_data import generate_data_profile
    generate_data_profile(processed_filepath)
    from scripts.profile_of_translations import profile_translations
    profile_translations(processed_filepath)

if __name__ == "__main__":
    main()
