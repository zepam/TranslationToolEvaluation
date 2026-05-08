#!/usr/bin/env python3
"""Run the dataset analysis and table-generation pipeline.

This script runs the core profiling scripts first, then any remaining
`combine*.py` scripts, and finally any `createtable*.py` scripts in the
`scripts/` directory.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.profile_of_data import generate_data_profile


def run_python_script(script_path: Path, *args: str) -> None:
    """Run a Python script with the current interpreter and fail fast on error."""
    # print(f"Running {script_path.name}...")
    subprocess.run([sys.executable, str(script_path), *args], check=True)


def collect_scripts(pattern: str, exclude: set[str]) -> list[Path]:
    """Collect top-level scripts matching a glob pattern, excluding selected names."""
    return sorted(
        script_path
        for script_path in SCRIPTS_DIR.glob(pattern)
        if script_path.name not in exclude
    )


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments for the pipeline runner."""
    parser = argparse.ArgumentParser(
        description="Run the TranslationToolEvaluation analysis pipeline in a fixed order."
    )
    parser.add_argument(
        "--processed-root",
        type=Path,
        default=REPO_ROOT / "data" / "processed",
        help="Root processed-data directory to profile.",
    )
    return parser.parse_args()


def main() -> None:
    """Run the requested scripts in the requested order."""
    args = parse_args()

    if not args.processed_root.exists():
        raise FileNotFoundError(f"Processed root does not exist: {args.processed_root}")

    # Run the requested core scripts first.
    print("Data profiling...")
    generate_data_profile(str(args.processed_root))

    run_python_script(SCRIPTS_DIR / "combine_data_profiles.py")
    run_python_script(SCRIPTS_DIR / "combine_per_lang_profile.py")

    already_run = {
        "profile_of_data.py",
        "combine_data_profiles.py",
        "combine_per_lang_profile.py",
    }

    print("\nCombining data profiles...")
    # Then run any remaining scripts in the two requested families.
    for script_path in collect_scripts("combine*.py", already_run):
        run_python_script(script_path)
        already_run.add(script_path.name)

    print("\nGenerating tables...")
    for script_path in collect_scripts("createtable*.py", already_run):
        run_python_script(script_path)
        already_run.add(script_path.name)

    print("Pipeline completed successfully.")


if __name__ == "__main__":
    main()
