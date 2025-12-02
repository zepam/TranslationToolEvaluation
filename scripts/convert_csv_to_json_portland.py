# import csv
import json
import argparse
import pandas as pd
from pathlib import Path
from data.language_codes import language_codes

def convert_csv_to_jsonl(csv_path, lang_map=language_codes):

    df = pd.read_csv(csv_path)

    # make "English" check case-insensitive and normalize the column name to 'English'
    cols_lower = {c.lower(): c for c in df.columns}
    if "english" not in cols_lower:
        raise ValueError("CSV file must contain an 'English' column (case-insensitive).")
    actual_english = cols_lower["english"]
    if actual_english != "English":
        df = df.rename(columns={actual_english: "English"})
    
    # get the filename and scenario name
    p = Path(csv_path)
    scenario = p.stem.split("_", 1)[1]
    basename = p.stem
    json_filename = f"{basename}.jsonl"
    jsonl_path = p.parent / json_filename
    # jsonl_path = p.with_suffix(".jsonl")

    with open(jsonl_path, "w", encoding="utf-8") as out:
        for i, row in df.iterrows():

            source_text = row["English"]

            translations = {}
            for col, val in row.items():
                if col == "English":
                    continue
                if pd.isna(val):
                    continue
                if col in lang_map:
                    translations[lang_map[col]] = str(val)

            record = {
                "id": f"{scenario}_{i:03d}",
                "scenario": scenario,
                "source": {"lang": "eng", "text": source_text},
                "translations": translations
            }

            out.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"✓ Wrote {len(df)} records to {jsonl_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to JSONL translation dataset.")
    parser.add_argument("--csv", required=True, help="Input CSV file path")

    args = parser.parse_args()

    csv_file = "/home/jen/TranslationsDataset/data/raw/portland_911_outage.csv"

    # Load language mapping JSON
    with open(args.langmap, "r", encoding="utf-8") as f:
        lang_map = json.load(f)

    #convert_csv_to_jsonl(args.csv)
    convert_csv_to_jsonl(csv_file, lang_map=lang_map)
