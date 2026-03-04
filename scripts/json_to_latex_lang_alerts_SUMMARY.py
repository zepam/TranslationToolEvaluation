import json
import statistics
from pathlib import Path

#TODO replace And with &, In with in

# Paths
INPUT_PATH = Path("/home/jen/TranslationsDataset/data/processed/portland/portland_data_profile.json")
OUTPUT_DIR = INPUT_PATH.parent

FULL_TABLE_PATH = OUTPUT_DIR / "translations_per_alert_language_full.tex"
SUMMARY_TABLE_PATH = OUTPUT_DIR / "translations_per_alert_language_summary.tex"


def latex_escape(text: str) -> str:
    return text.replace("_", "\\_")


def generate_full_longtable(data: dict) -> str:
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


def generate_summary_table(data: dict) -> str:
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
        "\\textbf{\\# Lang.} & "
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
    lines.append("\\caption{Summary of translation document coverage by alert type.}")
    lines.append("\\label{tab:portland_translations_per_alert_lang_summary}")
    lines.append("\\end{table}")
    return "\n".join(lines)

def format_alert_type(alert_type: str) -> str:
    """Convert snake_case alert type to Title Case with spaces."""
    return alert_type.replace("_", " ").title()


def main():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        profile = json.load(f)

    data = profile["translations_per_alert_type_per_language"]

    full_table = generate_full_longtable(data)
    summary_table = generate_summary_table(data)

    with open(FULL_TABLE_PATH, "w", encoding="utf-8") as f:
        f.write(full_table)

    with open(SUMMARY_TABLE_PATH, "w", encoding="utf-8") as f:
        f.write(summary_table)

    print("LaTeX tables written:")
    print(f" - Full table:    {FULL_TABLE_PATH}")
    print(f" - Summary table: {SUMMARY_TABLE_PATH}")


if __name__ == "__main__":
    main()