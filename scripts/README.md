# Scripts Directory Documentation

This folder contains data ingestion, conversion, profiling, and LaTeX export utilities used to build and analyze the Translation Dataset.

## Core scripts

### Conversions

| File | Purpose | Typical input | Typical output |
| --- | --- | --- | --- |
| `convert_fcc_to_csv.py` | Converts FCC workbook sheets into normalized CSV format. | `data/raw/fcc/fcc_alerts.xlsx` | Per-sheet CSV files and converted workbook |
| `convert_csv_to_json_GENERIC.py` | Converts generic multilingual CSVs (`English` + language columns) into JSONL records. | Source CSV files | JSONL files in `data/processed/{source}/` |
| `analyze_all_data.py` | Runs all data analysis scripts  and creates latex tables | JSON/JSONL files | `data/processed/stats/` `data/processed/tables/`|

### Analysis script

| File | Purpose | Typical input | Typical output |
| --- | --- | --- | --- |
| `analyze_all_data.py` | Runs all data analysis scripts  and creates latex tables | JSON/JSONL files | `data/processed/stats/` `data/processed/tables/`|

These scripts below are called by `analyze_all_data.py`. The default file source location is data/processed, excluding all files in `stats` or `tables`.

| File | Purpose | Typical input | Typical output |
| --- | --- | --- | --- |
| `createtable_json_to_latex_lang_alerts.py` | Creates LaTeX alert-type + language tables from profile JSON. Default: `data/processed/combined_data_profile.json`| One or more `*_profile.json` files | `.tex` table files |
| `createtable_json_to_latex_lang_alerts_SUMMARY.py` | Produces full + summary LaTeX translation coverage/statistics tables. | Combined profile JSON | `translations_per_alert_language_full.tex`, `translations_per_alert_language_summary.tex` |
| `createtable_domain_counts_csv_to_latex.py` | Converts domain counts CSV into formatted LaTeX table. | `combined_data_profile.json` | `{source_prefix}_domain_counts_table.tex` |
| `combine_csv_lang_profiles_to_latex.py` | Converts combined per-language profile CSV into LaTeX table. | `combined_per_language_profile.csv` |  `combined_lang_profiles_table.tex` |
| `combine_data_profiles.py` | Merges multiple `*_data_profile.json` files into one combined profile from directory. | Folder containing JSONL files | `combined_data_profile.json` |
| `combine_per_lang_profile.py` | Generates per-language stats for combined multilingual data. | `TranslationsDataset/data/processed` | `combined_per_language_profile.csv` |
| `profile_of_data.py` | Computes dataset-wide stats, alignment, domain counts, and coverage. | JSON/JSONL files | CSV stats + summary JSON under `stats/` |
| `profile_of_translations.py` | Builds per-language document/token/vocabulary statistics. | JSONL files + language mapping | `{origin}_data_profile.json` |


### Very specific scripts you probably won't use

| File | Purpose | Typical input | Typical output |
| --- | --- | --- | --- |
| `access_ipaws_archive.py` | Downloads archived IPAWS alerts from FEMA API. | FEMA IPAWS endpoint | `data/raw/ipaws_archived_alerts.jsonl` |
| `scripts/helpers/confirm_arabic_text.py` | Evaluates arabic text to confirm if it is formatted correctly | paste text into variables in code | True or False |

## Notes

- Most scripts rely on default paths rooted at this repository (for example under `data/raw`, `data/processed`, `metadata`, and `stable`).
- Several scripts require `pandas`; tokenization/profile scripts may also require `regex`.
- Event alias normalization is driven by `metadata/event_combinations.json`.
