#!/usr/bin/env python3
"""
find_mismatch_sentences.py

Scan sentence-delimited CSVs and report missing/extra/unique sentences across languages.

Usage:
  python find_mismatch_sentences.py

Assumes:
  - Input CSVs are in data/raw/fcc_sentencedelimited
  - Each CSV row is a sentence-aligned row (English and other languages)
  - English column header is 'English' (change ENGLISH_COL below if different)
"""
import csv
from pathlib import Path
import pandas as pd
import re
from IPython.display import display

# ---------- CONFIG ----------
INPUT_DIR = Path("data/raw/fcc_sentencedelimited")   # folder holding aligned CSVs (one row per sentence)
OUTPUT_DIR = Path("analysis_out")
CSV_GLOB = "*.csv"             # pattern to find aligned CSVs (adjust if needed)
ENGLISH_COL = "English"        # header name for English column
MIN_NONEMPTY_LEN = 1           # threshold for considering cell non-empty after strip
OUTPUT_REPORT = OUTPUT_DIR / "missing_extra_report.csv"
# ---------------------------------------------------

if 'INPUT_DIR' not in globals() or 'OUTPUT_DIR' not in globals():
    raise RuntimeError("Please set INPUT_DIR and OUTPUT_DIR Path variables in the notebook.")

INPUT_DIR = Path(INPUT_DIR)
OUTPUT_DIR = Path(OUTPUT_DIR)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def is_nonempty_cell(s):
    return bool(str(s).strip()) and len(str(s).strip()) >= MIN_NONEMPTY_LEN

report_rows = []
summary = {}  # file -> counts

files = sorted(INPUT_DIR.glob(CSV_GLOB))
print("Found {} files in {}".format(len(files), INPUT_DIR))

for f in files:
    try:
        df = pd.read_csv(f, dtype=str).fillna("")
    except Exception as e:
        print("Skipping {} (read error): {}".format(f.name, e))
        continue
    cols = list(df.columns)
    if ENGLISH_COL not in cols:
        print("Skipping {} (no '{}' column)".format(f.name, ENGLISH_COL))
        continue

    other_cols = [c for c in cols if c != ENGLISH_COL]
    file_counts = {"file": f.name, "missing_total": 0, "extra_total": 0, "rows_checked": len(df)}
    per_lang_missing = {c: 0 for c in other_cols}
    per_lang_extra = {c: 0 for c in other_cols}

    for row_idx, row in df.iterrows():
        eng_cell = row.get(ENGLISH_COL, "")
        eng_nonempty = is_nonempty_cell(eng_cell)

        for lang in other_cols:
            lang_cell = row.get(lang, "")
            lang_nonempty = is_nonempty_cell(lang_cell)

            if eng_nonempty and not lang_nonempty:
                # English present, translation missing
                report_rows.append({
                    "file": f.name,
                    "row_index": int(row_idx),
                    "issue": "missing_in_lang",
                    "language": lang,
                    "english_text": eng_cell.strip(),
                    "sentence_text": "",
                })
                file_counts["missing_total"] += 1
                per_lang_missing[lang] += 1

            elif (not eng_nonempty) and lang_nonempty:
                # English empty, but language has extra sentence
                report_rows.append({
                    "file": f.name,
                    "row_index": int(row_idx),
                    "issue": "extra_in_lang",
                    "language": lang,
                    "english_text": "",
                    "sentence_text": lang_cell.strip(),
                })
                file_counts["extra_total"] += 1
                per_lang_extra[lang] += 1

    # store per-file summary
    file_counts["per_lang_missing"] = per_lang_missing
    file_counts["per_lang_extra"] = per_lang_extra
    summary[f.name] = file_counts

# write report CSV
if report_rows:
    out_columns = ["file","row_index","issue","language","english_text","sentence_text"]
    with open(OUTPUT_REPORT, "w", encoding="utf-8", newline='') as outf:
        writer = csv.DictWriter(outf, fieldnames=out_columns)
        writer.writeheader()
        for r in report_rows:
            writer.writerow(r)
    print("Wrote detailed report:", OUTPUT_REPORT)
else:
    print("No missing/extra issues found across files.")

# Print concise summary
print("\nSummary per file:")
for fname, counts in summary.items():
    print(f"- {fname}: rows={counts['rows_checked']}, missing={counts['missing_total']}, extra={counts['extra_total']}")

# Optional: top offending languages across files
total_missing_by_lang = {}
total_extra_by_lang = {}
for counts in summary.values():
    for lang, c in counts['per_lang_missing'].items():
        total_missing_by_lang[lang] = total_missing_by_lang.get(lang,0) + c
    for lang, c in counts['per_lang_extra'].items():
        total_extra_by_lang[lang] = total_extra_by_lang.get(lang,0) + c

if total_missing_by_lang:
    print("\nTop languages by missing translations:")
    for lang, c in sorted(total_missing_by_lang.items(), key=lambda x: -x[1])[:10]:
        print(f"  {lang}: {c}")

if total_extra_by_lang:
    print("\nTop languages by extra translations:")
    for lang, c in sorted(total_extra_by_lang.items(), key=lambda x: -x[1])[:10]:
        print(f"  {lang}: {c}")

# show first few report rows in notebook (if any)
if report_rows:
    display(pd.read_csv(OUTPUT_REPORT).head(50))