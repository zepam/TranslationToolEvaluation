# script counts the records in a folder of jsonl files. save the results to a json file named "portland_data_profile.json" in the same folder. 
# count the number and type of alerts, number and name of languages, number of translations per alert per language, etc.

import json
from pathlib import Path

def profile_data(jsonl_folder):
    jsonl_folder = Path(jsonl_folder)
    if not jsonl_folder.is_dir():
        raise ValueError(f"{jsonl_folder} is not a valid directory.")

    profile = {
        "total_alerts": 0,
        "alert_types": set(),
        "languages": set(),
        "translations_per_alert": []
    }

    for jsonl_file in jsonl_folder.glob("*.jsonl"):
        with open(jsonl_file, "r", encoding="utf-8") as f:
            for line in f:
                record = json.loads(line)
                profile["total_alerts"] += 1
                alert_type = record.get("scenario", "unknown")
                profile["alert_types"].add(alert_type)
                translations = record.get("translations", {})
                profile["languages"].update(translations.keys())
                # profile["translations_per_alert"].append(len(translations))
                
                # Count translations per alert type per language
                if "translations_per_alert_type_per_language" not in profile:
                    profile["translations_per_alert_type_per_language"] = {}
                if alert_type not in profile["translations_per_alert_type_per_language"]:
                    profile["translations_per_alert_type_per_language"][alert_type] = {}
                
                for lang in translations.keys():
                    if lang not in profile["translations_per_alert_type_per_language"][alert_type]:
                        profile["translations_per_alert_type_per_language"][alert_type][lang] = 0
                    profile["translations_per_alert_type_per_language"][alert_type][lang] += 1

    # Convert sets to lists for JSON serialization
    profile["alert_types"] = list(profile["alert_types"])
    profile["languages"] = list(profile["languages"])

    # Save the profile to a JSON file
    output_path = jsonl_folder / "portland_data_profile.json"
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(profile, out, indent=4)

    print(f"Data profile saved to {output_path}")

def main():
    jsonl_folder = "data/processed/portland"
    profile_data(jsonl_folder)

if __name__ == "__main__":
    main()