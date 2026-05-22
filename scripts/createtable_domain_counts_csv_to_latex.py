"""
Convert a CSV file to a formatted LaTeX table.

This function reads a CSV file, applies text transformations (replacing underscores
with spaces and capitalizing appropriately), and generates a formatted LaTeX table
with bolded headers, custom column alignment, and caption/label.

Args:
    csv_file (str): Path to the input CSV file.
    output_file (str, optional): Path to write the LaTeX table output. If None,
        the table is printed to stdout. Defaults to None.
Returns:
    None: Outputs the LaTeX table either to a file or prints it.
Notes:
    - Column headers and data cells have underscores replaced with spaces
    - Headers are formatted with title case (with lowercase exceptions for 'and', 'in')
    - First column is left-aligned, all other columns are right-aligned
    - Column headers are bolded in the output
    - Table is wrapped with LaTeX table environment and centered
    - Includes caption: "Count of translation per each event type"
    - Includes label: "tab:combined_domain_counts"
"""


# convert the data profile domain counts CSV to a LaTeX table
import json
import pandas as pd
import re
import sys
from pathlib import Path

EVENT_COMBINATIONS_PATH = Path(__file__).resolve().parent.parent / "metadata" / "event_combinations.json"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tables"


def load_event_combinations(path=EVENT_COMBINATIONS_PATH):
    """Load alias -> canonical event mapping from JSON file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def domain_counts(csv_file, output_file=None, table_label="tab:domain_counts"):
    df = pd.read_csv(csv_file)

    event_map = load_event_combinations()
    if event_map and "scenario" in df.columns and "count" in df.columns:
        df["scenario"] = df["scenario"].map(lambda x: event_map.get(x, x))
        df = df.groupby("scenario", as_index=False)["count"].sum()

    if "scenario" in df.columns:
        df = df.sort_values("scenario", ascending=True)

    # Replace underscores with spaces and capitalize every word
    df = df.apply(lambda col: col.str.replace('_', ' ').str.title().str.replace('And', 'and').str.replace('In', 'in') if col.dtype == 'object' else col)
    
    df.columns = df.columns.str.replace('_', ' ').str.title()
    latex_table = df.to_latex(index=False, escape=False)
    
    # Bold the column headers
    lines = latex_table.split('\n')
    for i, line in enumerate(lines):
        if ' & ' in line and '\\' in line:
            # This is the header row
            headers = [h.strip() for h in line.split('&')]
            bold_headers = []
            for j, h in enumerate(headers):
                h = h.strip()
                # Remove row terminator from the last header before wrapping in \textbf{}
                if j == len(headers) - 1:
                    h = h.rstrip('\\').strip()
                    bold_headers.append(f'\\textbf{{{h}}} \\\\')
                else:
                    bold_headers.append(f'\\textbf{{{h}}}')
            lines[i] = ' & '.join(bold_headers)
            break
    latex_table = '\n'.join(lines)
    
    
    # Left align first column, right align all others. 
    col_format = 'l' + 'r' * (len(df.columns) - 1)

    latex_table = re.sub(r'\\begin{tabular}\{[^}]+\}', f'\\\\begin{{tabular}}{{{col_format}}}', latex_table)

    latex_table = '\\begin{table}\n\\centering\n' + latex_table + '\n\\end{table}'
    
    # Add gray background to header row
    latex_table = latex_table.replace('\\caption{Domain Counts}', '')
    latex_table = latex_table.replace(
        '\\end{tabular}',
        f'\\end{{tabular}}\n\\caption{{Count of translation per each event type}}\n\\label{{{table_label}}}'
    )
    
   
    if output_file:
        with open(output_file, 'w') as f:
            f.write(latex_table)
        # print(f"Wrote LaTeX table to {output_file}")
    else:
        print(latex_table)


def build_combined_domain_counts(processed_root, output_csv):
    """Build a combined domain_counts.csv by summing per-source stats files."""
    # domain_files = sorted(processed_root.glob("**/*_domain_counts.csv"))
    test = output_csv.parent / "stats"
    domain_files = sorted(output_csv.parent.glob("*_domain_counts.csv"))
    if not domain_files:
        raise FileNotFoundError(f"No per-source *_domain_counts.csv files found under {processed_root}")

    frames = [pd.read_csv(path) for path in domain_files]
    combined = (
        pd.concat(frames, ignore_index=True)
        .groupby("scenario", as_index=False)["count"]
        .sum()
        .sort_values("count", ascending=False)
    )

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(output_csv, index=False)
    print(f"Built combined domain counts from {len(domain_files)} files: {output_csv}")
    return output_csv

def make_beautiful_files():
    # data_source = (
    #     Path(sys.argv[1])
    #     if len(sys.argv) > 1
    #     else Path("data/processed/combined_data_profile.json")
    # )

    data_source = Path("data/processed/combined_data_profile.json")
    source_prefix = data_source.stem.replace("_data_profile", "")
    base_dir = data_source.parent.parent

    combined_csv = base_dir / "stats" / "domain_counts.csv"

    if source_prefix == "combined" and not combined_csv.exists():
        combined_csv = build_combined_domain_counts(base_dir, combined_csv)

    # Fallback for non-combined sources that do not have stats yet.
    # if not input_csv.exists():
    #     input_csv = Path("data/processed/portland/stats/domain_counts.csv")

    output_dir = base_dir.parent / "tables"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_tex = output_dir / f"{source_prefix}_domain_counts_table.tex"
    domain_counts(combined_csv, output_tex, table_label=f"tab:domain_counts_{source_prefix}")

    print("LaTeX tables written:")
    print(f" - Domain counts:    {output_tex}")


def main():
    make_beautiful_files()
    

if __name__ == "__main__":
    main()