"""Combine all *_data_profile.json files under data/processed into one profile.

The script recursively discovers profile files, merges their counts, and writes a
single combined JSON file.
"""

import argparse
import json
from pathlib import Path


def find_profile_files(processed_root: Path) -> list[Path]:
    """Return sorted list of all profile files under processed_root."""
    return sorted(processed_root.rglob("*_data_profile.json"))


def merge_profile_into_combined(combined: dict, profile: dict) -> None:
    """Merge one profile dictionary into combined in place."""
    combined["total_alerts"] += int(profile.get("total_alerts", 0))

    combined_alert_types = set(combined.get("alert_types", []))
    combined_alert_types.update(profile.get("alert_types", []))
    combined["alert_types"] = sorted(combined_alert_types)

    combined_languages = set(combined.get("languages", []))
    combined_languages.update(profile.get("languages", []))
    combined["languages"] = sorted(combined_languages)

    per_alert = combined.setdefault("translations_per_alert", [])
    per_alert.extend(profile.get("translations_per_alert", []))

    combined_nested = combined.setdefault("translations_per_alert_type_per_language", {})
    profile_nested = profile.get("translations_per_alert_type_per_language", {})

    for alert_type, lang_counts in profile_nested.items():
        target_lang_counts = combined_nested.setdefault(alert_type, {})
        for language, count in lang_counts.items():
            target_lang_counts[language] = int(target_lang_counts.get(language, 0)) + int(count)


def combine_profiles(processed_root: Path, output_path: Path) -> dict:
    """Combine all matching profile files and write output JSON."""
    profile_files = find_profile_files(processed_root)
    if not profile_files:
        raise ValueError(f"No *_data_profile.json files found under {processed_root}")

    combined = {
        "total_alerts": 0,
        "alert_types": [],
        "languages": [],
        "translations_per_alert": [],
        "translations_per_alert_type_per_language": {},
        "source_profile_files": [],
        "profiles_combined": 0,
    }

    for profile_file in profile_files:
        with open(profile_file, "r", encoding="utf-8") as f:
            profile = json.load(f)

        merge_profile_into_combined(combined, profile)
        combined["source_profile_files"].append(str(profile_file.relative_to(processed_root.parent)))
        combined["profiles_combined"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=4)

    return combined


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="Combine all *_data_profile.json files in data/processed into one JSON file."
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=Path("data/processed"),
        help="Root directory to search for *_data_profile.json files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/processed/combined_data_profile.json"),
        help="Output path for combined profile JSON.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    combined = combine_profiles(args.processed_root, args.output)

    print(f"Combined {combined['profiles_combined']} profile files.")
    print(f"Total alerts: {combined['total_alerts']}")
    print(f"Alert types: {len(combined['alert_types'])}")
    print(f"Languages: {len(combined['languages'])}")
    print(f"Output written to: {args.output}")


if __name__ == "__main__":
    main()
