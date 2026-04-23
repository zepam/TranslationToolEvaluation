# Scripts Directory Documentation

This folder contains data ingestion, conversion, profiling, and LaTeX export utilities used to build and analyze the Translation Dataset.

## Contents

### Core scripts

| File | Purpose | Typical input | Typical output |
|---|---|---|---|
| `access_ipaws_archive.py` | Downloads archived IPAWS alerts from FEMA API. | FEMA IPAWS endpoint | `data/raw/ipaws_archived_alerts.jsonl` |
| `convert_fcc_to_csv.py` | Converts FCC workbook sheets into normalized CSV format. | `data/raw/fcc/fcc_alerts.xlsx` | Per-sheet CSV files and converted workbook |
| `csv_to_json_GENERIC.py` | Converts generic multilingual CSVs (`English` + language columns) into JSONL records. | Source CSV files | JSONL files in `data/processed/{source}/` |
| `combine_data_profiles.py` | Merges multiple `*_data_profile.json` files into one combined profile from directory. | Folder containing JSONL files | `combined_data_profile.json` |
| `profile_of_data.py` | Computes dataset-wide stats, alignment, domain counts, and coverage. | JSON/JSONL files | CSV stats + summary JSON under `stats/` |
| `profile_of_translations.py` | Builds per-language document/token/vocabulary statistics. | JSONL files + language mapping | `{origin}_data_profile.json` |
| `create_latex_tables.py` | Orchestrates generation of LaTeX tables from processed profiles using helper scripts. | default: `data/processed/combined_data_profile.json` | Multiple `.tex` outputs |
| `combined_per_lang_profile.py` | Generates per-language stats for combined multilingual data. | `TranslationsDataset/data/processed` | `combined_per_language_profile.csv` |
| `combined_csv_lang_profiles_to_latex.py` | Converts combined per-language profile CSV into LaTeX table. | `combined_per_language_profile.csv` |  `combined_lang_profiles_table.tex` |

### Helper scripts

| File | Purpose | Typical input | Typical output |
|---|---|---|---|
| `json_to_latex_lang_alerts.py` | Creates LaTeX alert-type + language tables from profile JSON. Default: `data/processed/combined_data_profile.json`| One or more `*_profile.json` files | `.tex` table files |
| `json_to_latex_lang_alerts_SUMMARY.py` | Produces full + summary LaTeX translation coverage/statistics tables. | Combined profile JSON | `translations_per_alert_language_full.tex`, `translations_per_alert_language_summary.tex` |
| `domain_counts_csv_to_latex.py` | Converts domain counts CSV into formatted LaTeX table. | `combined_data_profile.json` | `{source_prefix}_domain_counts_table.tex` |

## Inferred pipeline order (Portland)

The scripts suggest this execution sequence:

1. `custom_portland/csv_to_json_portland.py`
2. `portland_tokenization.py`
3. `portland_per_lang_profile.py`
4. `portland_csv_lang_profiles_to_latex.py`
5. `profile_of_data.py`
6. `json_to_latex_lang_alerts.py`
7. `json_to_latex_lang_alerts_SUMMARY.py`

`portland_process_everything.py` orchestrate parts of this flow.

## Notes

- Most scripts rely on default paths rooted at this repository (for example under `data/raw`, `data/processed`, `metadata`, and `stable`).
- Several scripts require `pandas`; tokenization/profile scripts may also require `regex`.
- Event alias normalization is driven by `metadata/event_combinations.json`.
