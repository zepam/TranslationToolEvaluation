"""Generate LaTeX tables summarizing translation coverage by alert type and language.

Processes data profile JSON to produce two LaTeX table outputs:
1. Full longtable: Complete listing of translation counts per alert type/language
2. Summary table: Statistical summary (total, count, min, median, max) by alert type

Supports long tables spanning multiple pages and compact summary statistics tables
with proper LaTeX formatting including captions and labels.

Output files:
    - translations_per_alert_language_full.tex: Complete cross-tabulation
    - translations_per_alert_language_summary.tex: Summary statistics
"""
import json
import os
import statistics
import sys
from pathlib import Path

#TODO: Replace "And" with "&", "In" with "in" in formatted text

# Paths
DEFAULT_INPUT_PATH = Path("/home/jen/TranslationsDataset/data/processed/combined_data_profile.json")
EVENT_COMBINATIONS_PATH = Path(__file__).resolve().parent.parent / "metadata" / "event_combinations.json"


def load_event_combinations(path=EVENT_COMBINATIONS_PATH):
    """Load alias -> canonical event mapping from JSON file."""
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def combine_event_counts(translations, event_map):
    """Merge translation counts by canonical event type."""
    combined = {}
    for alert_type, lang_counts in translations.items():
        canonical = event_map.get(alert_type, alert_type)
        if canonical not in combined:
            combined[canonical] = {}
        for lang, count in lang_counts.items():
            combined[canonical][lang] = int(combined[canonical].get(lang, 0)) + int(count)
    return combined


def latex_escape(text: str) -> str:
    """Escape special characters for LaTeX.
    
    Escapes underscores by prepending a backslash. Used to safely include
    text in LaTeX documents without triggering underscore subscript syntax.
    
    Args:
        text (str): Text to escape.
    
    Returns:
        str: Text with underscores escaped as '\\_'.
    """
    return text.replace("_", "\\_")


def generate_full_longtable(data: dict) -> str:
    """Generate a full LaTeX longtable with all translation counts.
    
    Creates a multi-page longtable listing every alert type/language combination
    with its translation count. Includes proper headers, footers, and captions
    for handling page breaks in long tables.
    
    Args:
        data (dict): Nested dict {alert_type: {language: count}}.
    
    Returns:
        str: Complete LaTeX longtable source code with caption and label.
    """
    lines = []
    lines.append("\\begin{longtable}{p{3cm} p{3cm} r}")
    lines.append("\\caption{Number of translations per alert type and language} \\\\")
    lines.append("\\label{tab:translations_full} \\\\")
    lines.append("\\hline")
    lines.append("\\textbf{Alert\\\\Type} & \\textbf{Language} & \\textbf{N} \\\\")
    lines.append("\\hline")
    lines.append("\\endfirsthead")
    lines.append("")
    lines.append("\\hline")
    lines.append("\\textbf{Alert\\\\Type} & \\textbf{Language} & \\textbf{N} \\\\")
    lines.append("\\hline")
    lines.append("\\endhead")
    lines.append("")
    lines.append("\\hline")
    lines.append("\\endfoot")
    lines.append("")
    lines.append("\\hline")
    lines.append("\\endlastfoot")
    lines.append("")

    for alert_type in sorted(data.keys()):
        for language in sorted(data[alert_type].keys()):
            count = data[alert_type][language]
            # inside generate_full_longtable
            lines.append(
                f"{latex_escape(format_alert_type(alert_type))} & "
                f"{latex_escape(language)} & {count} \\\\"
            )

    lines.append("\\end{longtable}")
    return "\n".join(lines)


def generate_summary_table(data: dict, source_prefix: str) -> str:
    """Generate a LaTeX summary statistics table by alert type.
    
    Creates a compact summary table with one row per alert type, showing:
    total translations, count of languages covered, and distribution statistics
    (min, median, max translation counts across languages).
    
    Optimized for single-page display with compact spacing and professional
    formatting using booktabs rules.
    
    Args:
        data (dict): Nested dict {alert_type: {language: count}}.
    
    Returns:
        str: Complete LaTeX table source code with proper formatting.
    """
    lines = []
    lines.append("\\begin{table}")
    lines.append("\\centering")
    lines.append("\\setlength{\\tabcolsep}{3pt}")
    lines.append("\\renewcommand{\\arraystretch}{0.95}")
    lines.append("\\begin{tabular}{lrrrrr}")
    lines.append("\\toprule")
    lines.append(
        "\\textbf{Alert Type} & "
        "\\textbf{Total} & "
        "\\textbf{\\# Langs} & "
        "\\textbf{Min} & "
        "\\textbf{Median} & "
        "\\textbf{Max} \\\\"
    )
    lines.append("\\midrule")

    for alert_type in sorted(data.keys()):
        counts = list(data[alert_type].values())
        total = sum(counts)
        n_lang = len(counts)
        min_c = min(counts)
        max_c = max(counts)
        median_c = int(statistics.median(counts))

        # inside generate_summary_table
        lines.append(
            f"{latex_escape(format_alert_type(alert_type))} & "
            f"{total:,} & {n_lang} & {min_c} & {median_c} & {max_c} \\\\"
        )

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\caption{Summary of translation document language coverage by alert type.}")
    lines.append(f"\\label{{tab:{source_prefix}_translations_per_alert_lang_summary}}")
    lines.append("\\end{table}")
    return "\n".join(lines)

def format_alert_type(alert_type: str) -> str:
    """Convert snake_case alert type to Title Case with spaces.
    
    Transforms underscore-delimited strings to human-readable format by
    replacing underscores with spaces and applying title case capitalization.
    
    Args:
        alert_type (str): Alert type in snake_case format (e.g., 'power_outage').
    
    Returns:
        str: Formatted alert type (e.g., 'Power Outage').
    """
    return alert_type.replace("_", " ").title()


def main():
    """Main entry point for generating LaTeX translation summary tables.
    
    Loads translation data from JSON profile, generates both full and summary
    LaTeX tables, and writes them to their respective output files. Prints
    confirmation messages with output paths.
    
    Returns:
        None. Produces two .tex files in the output directory.
    """
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT_PATH
    source_prefix = input_path.stem.replace("_data_profile", "")
    output_dir = input_path.parent.parent / "tables"
    full_table_path = output_dir / f"{source_prefix}_translations_per_alert_language_full.tex"
    summary_table_path = output_dir / f"{source_prefix}_translations_per_alert_language_summary.tex"

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        profile = json.load(f)

    data_raw = profile["translations_per_alert_type_per_language"]
    data = combine_event_counts(data_raw, load_event_combinations())

    full_table = generate_full_longtable(data)
    summary_table = generate_summary_table(data, source_prefix)

    with open(full_table_path, "w", encoding="utf-8") as f:
        f.write(full_table)

    with open(summary_table_path, "w", encoding="utf-8") as f:
        f.write(summary_table)

    print("LaTeX tables written:")
    print(f" - Full table:    {os.path.relpath(full_table_path)}")
    print(f" - Summary table: {os.path.relpath(summary_table_path)}")


if __name__ == "__main__":
    main()