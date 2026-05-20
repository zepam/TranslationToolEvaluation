#!/usr/bin/env python3
import pandas as pd
import importlib.util
import json
from pathlib import Path

def load_language_codes_py(py_path: str, var_name: str = "langauge_codes") -> dict:
    spec = importlib.util.spec_from_file_location("language_codes_module", py_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return getattr(module, var_name)

def latex_escape(s: str) -> str:
    # minimal escaping for table cells
    return (s.replace("\\", r"\textbackslash{}").replace("&", r"\&").replace("%", r"\%").replace("$", r"\$").replace("#", r"\#").replace("_", r"\_").replace("{", r"\{").replace("}", r"\}")
            )

def format_int(x):
    try:
        return f"{int(x):,}"
    except Exception:
        return str(x)

def format_float(x, nd=2):
    try:
        return f"{float(x):.{nd}f}"
    except Exception:
        return str(x)


def load_language_flags(path: str) -> tuple[set[str], set[str]]:
    """Load low-resource and not-in-NLLB language sets from JSON."""
    p = Path(path)
    if not p.exists():
        return set(), set()

    data = json.loads(p.read_text(encoding="utf-8"))
    low_resource = set(data.get("low_resource", []))
    not_in_nllb = set(data.get("not_in_nllb", []))
    return low_resource, not_in_nllb

def main():
    import argparse
    ap = argparse.ArgumentParser()
    # ap.add_argument("--csv", required=True, help="Input per-language CSV (from profiler)")
    ap.add_argument("--csv", default="data/processed/stats/combined_per_language_profile.csv", help="Input per-language CSV (from profiler)")
    ap.add_argument("--lang-codes-py", default="/home/jen/TranslationsDataset/data/language_codes.py",
                    help="Path to language_codes.py")
    # ap.add_argument("--out-tex", required=True, help="Output.tex file")
    ap.add_argument("--out-tex", default="data/processed/tables/combined_lang_profiles_table.tex", help="Output.tex file")
    ap.add_argument("--table-label", default="tab:combined_per_language_stats", help="LaTeX label")
    ap.add_argument("--table-caption", default="Statistics per language: Number of documents, Number of Sentences, Tokens, Characters, Average Tokens per Sentence, Average Characters per Sentence, Vocabulary Size.", help="Caption")
    ap.add_argument("--language-flags", default="metadata/language_flags.json", help="Path to JSON with low_resource and not_in_nllb lists")
    ap.add_argument("--sort-by", default="Language Name", help="Column to sort by")
    args = ap.parse_args()

    # Load CSV
    df = pd.read_csv(args.csv)

    # Expect these columns from profiler:
    # Language Name, Lang Code, Num of Docs, Num of Sentences, Num of Tokens, Num of Characters,
    # Avg Tokens per Sentence, Avg Characters per Sentence, Vocabulary Size
    # Normalize column names to match the figure
    rename = {
        "Num of Sentences": "Sents",
        "Num of Tokens": "Tokens",
        "Num of Characters": "Chars",
        "Avg Tokens per Sentence": "Avg Tokens per Sent",
        "Avg Characters per Sentence": "Avg Chars per Sent",
        "Vocabulary Size": "Vocab Size"
    }
    df = df.rename(columns=rename)

    # Load mapping (LanguageName -> iso codes)
    lang_codes = load_language_codes_py(args.lang_codes_py, var_name="language_codes")

    # Build reverse lookup: map BCP-47, iso639-2, iso639-1 codes to their info dict
    # only two languages have a BCP-47 code, check for that first when deciding what to display in the table
    reverse_lookup = {}
    for lang_name, info in lang_codes.items():
        if isinstance(info, dict):
            for code_type in ["BCP-47", "iso639-2", "iso639-1"]:
                code = info.get(code_type)
                if code:
                    reverse_lookup[code] = info

    # Build a name -> displayed code mapping for the LaTeX table:
    # prefer BCP-47 if present, else iso639-2, else iso639-1, else keep the existing code.
    def display_code(row):
        name = str(row["Language Name"])
        info = lang_codes.get(name) or reverse_lookup.get(name)
        print(f"Processing language '{name}' with info: {info}")
        
        if isinstance(info, dict):
            return info.get("BCP-47") or info.get("iso639-2") or info.get("iso639-1") or row["Lang Code"]
        return row["Lang Code"]

    df["Lang Code"] = df.apply(display_code, axis=1)

    low_resource_langs, not_in_nllb_langs = load_language_flags(args.language_flags)

    def name_with_markers(name: str) -> str:
        marker = ""
        if name in low_resource_langs:
            marker += "*"
        if name in not_in_nllb_langs:
            marker += "#"
        return f"{name}{marker}"

    df["Language Name"] = df["Language Name"].apply(name_with_markers)

    # Sort
    if args.sort_by in df.columns:
        df = df.sort_values(args.sort_by, ascending=True)

    # Column order like figure
    cols = [
        "Language Name", "Lang Code", "Num of Docs", "Sents", "Tokens", "Chars",
        "Avg Tokens per Sent", "Avg Chars per Sent", "Vocab Size"
    ]
    df = df[cols]

    # Format values and escape LaTeX
    lines = []
    header = (
        r"\begin{table}[t]" "\n"
        r"\centering" "\n"
        r"\small" "\n"
        r"\setlength{\tabcolsep}{4pt}" "\n"
        r"\begin{tabular}{l l r r r r r r r}" "\n"
        r"\toprule" "\n"
        r"\textbf{Language} & \textbf{Lang} & \textbf{Num of} & \textbf{Sents} & \textbf{Tokens} & \textbf{Chars} & "
        r"\textbf{Avg Tokens} & \textbf{Avg Chars} & \textbf{Vocab} \\" "\n"
        r"\textbf{Name} & \textbf{Code} & \textbf{Docs} &  &  &  & "
        r"\textbf{per Sent} & \textbf{per Sent} & \textbf{Size} \\" "\n"
        r"\midrule" "\n"
    )
    lines.append(header)

    for _, row in df.iterrows():
        lang = latex_escape(str(row["Language Name"]))
        code = latex_escape(str(row["Lang Code"]))

        ndocs = format_int(row["Num of Docs"])
        sents = format_int(row["Sents"])
        toks = format_int(row["Tokens"])
        chars = format_int(row["Chars"])
        avg_toks = format_float(row["Avg Tokens per Sent"], 2)
        avg_chars = format_float(row["Avg Chars per Sent"], 2)
        vocab = format_int(row["Vocab Size"])

        lines.append(f"{lang} & {code} & {ndocs} & {sents} & {toks} & {chars} & {avg_toks} & {avg_chars} & {vocab} \\\\\n")

    footer = (
        r"\bottomrule" "\n"
        r"\end{tabular}" "\n"
        rf"\caption{{{(args.table_caption)} *: indicated as low resource in NLLB paper or due to lack of Google Translate coverage. \#: not included in NLLB.}}" "\n"
        rf"\label{{{(args.table_label)}}}" "\n"
        # r"\end{tabular}" "\n"
        r"\end{table}" "\n"
    )
    lines.append(footer)

    # create output directory if it doesn't exist
    out_dir = Path(args.out_tex).parent
    out_dir.mkdir(parents=True, exist_ok=True)

    Path(args.out_tex).write_text("".join(lines), encoding="utf-8")
    print(f"Wrote LaTeX table to {args.out_tex}")

if __name__ == "__main__":
    main()