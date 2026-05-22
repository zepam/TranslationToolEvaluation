"""Combine per-source profile JSON files into one aggregate profile.

This script searches a processed-data directory for files matching
``*_data_profile.json``, merges their summary fields, and writes a single
``combined_data_profile.json`` output.

Expected input profile keys (missing keys are treated as empty/zero):
- ``total_alerts``: integer alert count for that source profile
- ``alert_types``: list of alert type labels
- ``languages``: list of language codes
- ``translations_per_alert``: list of per-alert translation counts
- ``translations_per_alert_type_per_language``: nested mapping of the form
    ``{alert_type: {language: count}}``

Merge behavior:
- Numeric totals are summed.
- ``alert_types`` and ``languages`` are deduplicated and sorted.
- ``translations_per_alert`` entries are concatenated.
- Nested ``translations_per_alert_type_per_language`` counts are summed by
    alert type and language.

Usage:
        python scripts/combine_data_profiles.py
        python scripts/combine_data_profiles.py --processed-root data/processed --output data/processed/combined_data_profile.json
"""

import argparse
import json
from pathlib import Path


def find_profile_files(processed_root: Path) -> list[Path]:
    """Find all profile files under the processed root.
    Args:
        processed_root: Directory to recursively search.
    Returns:
        Sorted list of paths that match ``*_data_profile.json`` and do not
        begin with ``combined``.
    """
    return sorted(
        path
        for path in processed_root.rglob("*_data_profile.json")
        if not path.name.startswith("combined")
    )


def merge_profile_into_combined(combined: dict, profile: dict) -> None:
    """Merge one profile dictionary into a combined accumulator in place.
    Args:
        combined: Mutable aggregate profile dictionary that is updated.
        profile: Single input profile dictionary to merge into ``combined``.
    Notes:
        This function is intentionally tolerant of partial input profiles and
        defaults missing values to zero/empty collections.
    """
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
    """Combine discovered profile files and write one JSON output.
    Args:
        processed_root: Directory containing per-source profile files.
        output_path: Destination JSON path for the merged profile.
    Returns:
        The in-memory combined profile dictionary that was written to disk.
    Raises:
        ValueError: If no matching profile files are found.
    """
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
        # Store source file paths relative to repository root for traceability.
        combined["source_profile_files"].append(str(profile_file.relative_to(processed_root.parent)))
        combined["profiles_combined"] += 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(combined, f, indent=4)

    return combined


def parse_args() -> argparse.Namespace:
    """Build and parse command-line arguments for the script."""
    parser = argparse.ArgumentParser(
        description="Combine all *_data_profile.json files in data/processed into one JSON file."
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=Path("data/stats"),
        help="Root directory to search for *_data_profile.json files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/stats/combined_data_profile.json"),
        help="Output path for combined profile JSON.",
    )
    return parser.parse_args()


def main() -> None:
    """Run CLI entrypoint and print a compact merge summary."""
    args = parse_args()
    combined = combine_profiles(args.processed_root, args.output)

    print(f"Combined {combined['profiles_combined']} profile files.")
    print(f"Total alerts: {combined['total_alerts']}")
    print(f"Alert types: {len(combined['alert_types'])}")
    print(f"Languages: {len(combined['languages'])}")
    print(f"Output written to (combine_data_files): {args.output}")


if __name__ == "__main__":
    main()
