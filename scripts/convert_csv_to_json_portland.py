# import csv
import json
import pandas as pd
from pathlib import Path
import sys

# Ensure the project root is on sys.path so the `data` package can be imported
# when this script is executed directly from the `scripts/` directory.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    
    # get the filepath, filename, and scenario name
    p = Path(csv_path)
    parent_filepath = p.parent
    scenario = p.stem.split("_", 1)[1]
    origin = p.stem.split("_", 1)[0]
    basename = p.stem
    json_filename = f"{basename}.jsonl"
    processed_filepath= parent_filepath.parent.parent / "processed"
    processed_filepath.mkdir(parents=True, exist_ok=True)
    jsonl_path = processed_filepath / json_filename

    records = []
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

        convert_csv_to_jsonl(Path(csv_file), lang_map=language_codes)

if __name__ == "__main__":
    main()
