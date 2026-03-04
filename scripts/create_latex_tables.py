"""
Execute a series of scripts to generate LaTeX tables from translation data.
This function orchestrates the creation of LaTeX tables by running multiple
helper scripts in sequence. It requires a data source argument to be passed
via command line and processes translation data through three conversion scripts.

Command Line Arguments:
    data_source (str): The path or identifier for the data source containing
                        translation metrics and language alert information.

Raises:
    SystemExit: If insufficient command line arguments are provided or if any
                of the called scripts fail during execution.

Example:
    python create_latex_tables.py /path/to/data_source
"""

import subprocess
import sys
from pathlib import Path

def main():
    # if len(sys.argv) < 2:
    #     print("Usage: python create_latex_tables.py <data_source>")
    #     sys.exit(1)
    
    # data_source = sys.argv[1]

    data_source = "/home/jen/TranslationsDataset/data/processed/portland/portland_data_profile.json"
    script_dir = Path(__file__).parent
    
    scripts = [
        "json_to_latex_lang_alerts.py",
        "json_to_latex_lang_alerts_SUMMARY.py",
        "domain_counts_csv_to_latex.py"
    ]
    
    for script in scripts:
        try:
            print(f"Running {script} with data source: {data_source}")
            subprocess.run([
                sys.executable,
                script_dir / script,
                data_source
            ], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {script} failed with exit code {e.returncode}")
            sys.exit(1)
    
    print("All scripts completed successfully!")

if __name__ == "__main__":
    main()