# script counts the records in a folder of jsonl files. save the results to a json file named "portland_data_profile.json" in the same folder. 
# count the number and type of alerts, number and name of languages, number of translations per alert per language, etc.

import json
from pathlib import Path
import sys

# Add parent directory to path to import language_codes
sys.path.insert(0, str(Path(__file__).parent.parent / "data"))
from language_codes import language_codes

def profile_translations(jsonl_folder):
    jsonl_folder = Path(jsonl_folder)
    if not jsonl_folder.is_dir():
        raise ValueError(f"{jsonl_folder} is not a valid directory.")
    
    origin = jsonl_folder.name

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

                #
                
                for lang in translations.keys():
                    if lang not in profile["translations_per_alert_type_per_language"][alert_type]:
                        profile["translations_per_alert_type_per_language"][alert_type][lang] = 0
                    profile["translations_per_alert_type_per_language"][alert_type][lang] += 1

    # Convert sets to lists for JSON serialization
    profile["alert_types"] = list(profile["alert_types"])
    profile["languages"] = list(profile["languages"])

    # Create reverse mapping from code to language name
    # convert_language_codes(profile)

    # Save the profile to a JSON file
    output_path = jsonl_folder.parent.parent / "stats" / f"{origin}_data_profile.json"
    with open(output_path, "w", encoding="utf-8") as out:
        json.dump(profile, out, indent=4)

    print(f"Data profile saved to {output_path}")

def convert_language_codes(profile):
    code_to_name = {v: k for k, v in language_codes.items()}
    
    # Convert language codes to names
    profile["languages"] = [code_to_name.get(code, code) for code in profile["languages"]]
    
    # Convert codes to names in translations_per_alert_type_per_language
    new_translations_per_alert = {}
    for alert_type, lang_counts in profile["translations_per_alert_type_per_language"].items():
        new_translations_per_alert[alert_type] = {}
        for code, count in lang_counts.items():
            lang_name = code_to_name.get(code, code)
            new_translations_per_alert[alert_type][lang_name] = count
    profile["translations_per_alert_type_per_language"] = new_translations_per_alert

def main(jsonl_folder=None):
    if jsonl_folder is None:
        print("No jsonl_folder provided. Please provide the path to the folder containing the JSONL files.")
    profile_translations(jsonl_folder)

if __name__ == "__main__":
    main()