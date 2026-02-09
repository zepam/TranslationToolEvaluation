# Dataset: Portland Emergency & Public Safety Alerts

## Summary
- This folder contains raw CSV exports of public safety, emergency, and alert messages for the Portland region. Files cover multiple alert types and languages.

## Files
- portland_911_outage.csv
- portland_air_quality.csv
- portland_alert_and_warning.csv
- portland_boil_water.csv
- portland_dam_failure.csv
- portland_evacuation.csv
- portland_extreme_heat.csv
- portland_flood.csv
- portland_general.csv
- portland_power_lines.csv
- portland_power_outage.csv
- portland_reunification.csv
- portland_shelter_in_place.csv
- portland_shelters.csv
- portland_wildfire.csv
- portland_winter_weather.csv

## Provenance
- Source organization(s): The data is hosted by Portland Bureau of Emergency Management (http://www.portlandoregon.gov/pbem/). The content is managed by the Regional Disaster Preparedness Organization (http://www.rdpo.org/).
- Collection notes: CSVs are stored as raw exports in directory `data/raw/portland/`.
- Downloaded from https://www.publicalerts.org/messaging-tools. The <a href="https://docs.google.com/spreadsheets/d/1PCQVe6nANW9-ewCb8-osJ-C9BTkaIvmt_AYwbF0Pidg/edit?gid=841165143#gid=841165143" target="_blank" rel="noopener">original data file</a> was created on 11/14/24. File downloaded on 12/1/25. Original data file Critical_Safety_Messages-Combined_Library.xlsx available in this folder.

## Schema notes
- Column names and exact fields may vary between CSV files. Typical fields include the original message in English, followed by the translated message with one language per column.
- For exact column listings, look at each CSV file. Field presence/format may differ.

## Processing
- These CSV files were converted to newline-delimited JSON (`.jsonl`) and placed in `data/processed/` using the script `scripts/convert_csv_to_json_portland.py`.
- Encoding: CSVs are UTF-8 encoded.

## Related files
- Processing scripts: `scripts/convert_csv_to_json_portland.py`, `scripts/plumber.py`.
- Processed outputs: `data/processed/*.jsonl`.
- Dataset documentation: `metadata/dataset_card.md`, `metadata/datasheet.md`, and `metadata/schema.md`.
- Project config and language reference: `config/languages.yaml`, `config/settings.yaml`.

## License & Contact
- LICENSE NOT AVAILABLE
<!-- - License: see the repository `LICENSE.md` for licensing and redistribution terms.
- Contact / maintainer: see `README.md` for project owner and contact details. -->