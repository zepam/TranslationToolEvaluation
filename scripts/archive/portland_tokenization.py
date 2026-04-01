#!/usr/bin/env python3
"""Multilingual tokenization and token count statistics generator.

Processes JSONL files containing multilingual alert data and generates token-level
statistics by language and scenario. Produces JSON records with per-document token
counts and CSV summary statistics aggregated by scenario and language.

Supports multiple tokenization strategies: character-level for CJK and Southeast
Asian languages, word-level for alphabetic languages. Handles placeholders as
atomic tokens and deduplicates by preferring translations over source text.

Usage:
    python portland_tokenization.py \
      --in-dir /path/to/processed/alerts \
      --out-dir /path/to/output
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import regex as re
import pandas as pd

# -----------------------
# Placeholder normalization
# -----------------------
PLACEHOLDER_RE = re.compile(r"\{([^{}]*)\}")

def normalize_placeholders(text: str) -> str:
    """Normalize placeholder format in text.
    
    Standardizes placeholders by collapsing internal whitespace, converting
    placeholders containing letters or numbers to uppercase, and removing empty
    placeholders. Input None returns None unchanged.
    
    Args:
        text (str | None): Text containing placeholders in {key} format.
    
    Returns:
        str | None: Text with normalized placeholders.
    """
    if text is None:
        return text

    def repl(m):
        inner = re.sub(r"\s+", " ", m.group(1)).strip()
        if not inner:
            return "{}"
        if re.search(r"[\p{L}\p{N}]", inner):
            inner = inner.upper()
        return "{" + inner + "}"

    return PLACEHOLDER_RE.sub(repl, text)

# -----------------------
# Tokenization
# -----------------------
CJK_RE = re.compile(r'[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]')

# Keep placeholders as atomic tokens; otherwise letters/marks or numbers
WORDLIKE_OR_PLACEHOLDER_RE = re.compile(
    r"\{[^{}]+\}|[\p{L}\p{M}]+|\p{N}+",
    flags=re.UNICODE
)

def _char_tokens_keep_placeholders(s: str) -> List[str]:
    """Tokenize text into individual characters while preserving placeholders.
    
    Splits text into character tokens suitable for languages without word
    boundaries (CJK, Thai, Lao, Khmer, Burmese). Preserves {placeholder} sequences
    as single tokens and skips whitespace.
    
    Args:
        s (str): Text to tokenize.
    
    Returns:
        list[str]: List of character tokens and placeholder strings.
    """
    out: List[str] = []
    i = 0
    while i < len(s):
        if s[i] == "{":
            j = s.find("}", i + 1)
            if j != -1:
                out.append(s[i:j+1])
                i = j + 1
                continue
        if not s[i].isspace():
            out.append(s[i])
        i += 1
    return out

def tokenize_translation(text: str, lang_code: Optional[str] = None) -> List[str]:
    """Tokenize text with language-specific handling.
    
    Applies language-appropriate tokenization: character-level for CJK and
    Southeast Asian languages (Thai, Lao, Khmer, Burmese), word-level for others.
    Preserves placeholders as single tokens in all cases.
    
    Args:
        text (str | None): Text to tokenize.
        lang_code (str | None): ISO 639-1 or 639-2 language code (e.g., 'zh', 'en').
            Used to select appropriate tokenization strategy. Subcomponents after
            '-' are ignored (e.g., 'zh-Hans' -> 'zh').
    
    Returns:
        list[str]: List of word or character tokens. Returns empty list for
            None or empty input.
    """
    if text is None:
        return []
    t = normalize_placeholders(text).strip()
    if not t:
        return []

    primary = lang_code.strip().lower().split("-")[0] if lang_code else None

    # CJK -> character tokens
    if CJK_RE.search(t) or (primary in {"zh", "ja", "ko"}):
        return _char_tokens_keep_placeholders(t)

    # Thai/Lao/Khmer/Burmese -> char tokens (no-ICU fallback)
    if primary in {"th", "lo", "km", "my"}:
        return _char_tokens_keep_placeholders(t)

    # Default -> word-like tokens + placeholders
    return WORDLIKE_OR_PLACEHOLDER_RE.findall(t)

def build_doc_texts(obj: dict) -> dict:
    """Extract language->text mappings from an alert document.
    
    Builds a deduplicated mapping of language codes to text content. Translations
    take priority over source text. English source language code 'eng' is normalized
    to 'en'. Skips None or empty values.
    
    Handles multiple data formats: current data typically has English as source,
    but future data may have different sources with English as translation. This
    function adapts to both patterns.
    
    Args:
        obj (dict): Alert document with optional 'translations' and 'source' fields,
            each containing language code -> text mappings.
    
    Returns:
        dict: Mapping of normalized language codes to text strings. At most one
            text per language (translations preferred over source).
    """
    texts = {}

    translations = obj.get("translations") or {}
    if isinstance(translations, dict):
        for lang, txt in translations.items():
            if txt is not None and str(txt).strip():
                texts[lang] = txt

    source = obj.get("source") or {}
    if isinstance(source, dict):
        for lang, txt in source.items():
            if txt is None or not str(txt).strip():
                continue
            lang_norm = "en" if lang == "eng" else lang

            # only fill if translation not already present
            if lang_norm not in texts:
                texts[lang_norm] = txt

    return texts

# -----------------------
# Folder processing
# -----------------------
def iter_jsonl_records(folder: Path):
    """Iterate through JSON objects from JSONL files in a directory.
    
    Loads JSONL files (not recursive) in alphabetical order. Yields file path,
    line number, and parsed object for each line. Skips empty lines and silently
    ignores lines with JSON parsing errors.
    
    Args:
        folder (Path): Directory containing .jsonl files.
    
    Yields:
        tuple: (filepath, line_num, obj) where filepath is the source file Path,
            line_num is the 1-based line number, and obj is the parsed JSON dict.
    """
    # ONLY files directly in `folder`, not subfolders
    for fp in sorted(folder.glob("*.jsonl")):
        with fp.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                    yield fp, line_num, obj
                except json.JSONDecodeError:
                    continue

def process_folder(in_dir: str, out_dir: str) -> None:
    """Process JSONL folder and generate tokenization statistics.
    
    Reads JSONL files from the input directory and generates tokenization
    statistics. If `in_dir` points to a `processed` root, this function will
    process all immediate subfolders except `stats` and `tables`.
    
    Args:
        in_dir (str): Directory containing .jsonl alert files to process, or a
            processed root directory containing source subfolders.
        out_dir (str): Output directory for results. Created if missing.
    
    Returns:
        None. Produces two output files:
            - token_counts.records.jsonl: Per-document record with token counts
            - token_counts.summary.csv: Aggregated statistics by scenario/language
    """
    in_dir_p = Path(in_dir)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    # If pointed at processed/, process each source subfolder except stats/tables.
    excluded = {"stats", "tables"}
    if in_dir_p.name == "processed":
        folders_to_process = [
            p for p in sorted(in_dir_p.iterdir())
            if p.is_dir() and p.name not in excluded
        ]
    else:
        folders_to_process = [in_dir_p]

    jsonl_out = out_dir_p / "token_counts.records.jsonl"
    csv_out = out_dir_p / "token_counts.summary.csv"

    # Aggregation accumulators
    total_by_lang = {}
    total_by_scenario_lang = {}  # (scenario, lang) -> tokens
    docs_by_scenario = {}        # scenario -> docs
    docs_by_lang = {}            # lang -> docs containing that lang
    docs_by_scenario_lang = {}   # (scenario, lang) -> docs containing that lang

    num_records = 0

    with jsonl_out.open("w", encoding="utf-8") as fout:
        for folder in folders_to_process:
            for fp, line_num, obj in iter_jsonl_records(folder):
                # print (f"Processing {fp} (line {line_num})...")
                num_records += 1
                rec_id = obj.get("id")
                scenario = obj.get("scenario") or obj.get("domain") or "UNKNOWN"

                texts = build_doc_texts(obj)  # <-- uses translations + source without double counting
                token_counts: Dict[str, int] = {}

                # doc counters
                docs_by_scenario[scenario] = docs_by_scenario.get(scenario, 0) + 1

                for lang_code, txt in texts.items():

                # translations = obj.get("translations", {}) or {}
                # token_counts: Dict[str, int] = {}

                # # doc counters
                # docs_by_scenario[scenario] = docs_by_scenario.get(scenario, 0) + 1

                # for lang_code, txt in translations.items():
                    # print (f"  Tokenizing {lang_code}: {txt[:100]}...")
                    toks = tokenize_translation(txt, lang_code=lang_code)
                    n = len(toks)
                    token_counts[lang_code] = n

                    # totals
                    total_by_lang[lang_code] = total_by_lang.get(lang_code, 0) + n
                    key = (scenario, lang_code)
                    total_by_scenario_lang[key] = total_by_scenario_lang.get(key, 0) + n

                    # doc presence counts
                    docs_by_lang[lang_code] = docs_by_lang.get(lang_code, 0) + 1
                    docs_by_scenario_lang[key] = docs_by_scenario_lang.get(key, 0) + 1

                out_rec: Dict[str, Any] = {
                    "id": rec_id,
                    "scenario": scenario,
                    "source_file": str(fp),
                    "token_counts": token_counts
                }
                fout.write(json.dumps(out_rec, ensure_ascii=False) + "\n")

    # Build summary CSV
    print("Building summary CSV...")
    rows = []
    for (scenario, lang), tok_total in total_by_scenario_lang.items():
        doc_count = docs_by_scenario_lang.get((scenario, lang), 0)
        avg_tok_per_doc = (tok_total / doc_count) if doc_count else 0.0
        rows.append({
            "scenario": scenario,
            "language": lang,
            "docs_with_language": doc_count,
            "total_tokens": tok_total,
            "avg_tokens_per_doc": round(avg_tok_per_doc, 2)
        })

    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["scenario", "language"])
    df.to_csv(csv_out, index=False)

    print(f"Processed {num_records} records")
    print(f"Wrote JSONL: {jsonl_out}")
    print(f"Wrote CSV:   {csv_out}")

def main():
    """Command-line interface for tokenization pipeline.
    
    Parses arguments and runs the complete tokenization and statistics
    generation pipeline on the specified input directory.
    
    Command-line arguments:
        --in-dir: Directory containing .jsonl files, or `processed/` root
            containing source subfolders (default: processed).
        --out-dir: Output directory for results
            (default: processed/token_stats).
    """
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in-dir",
        default="/home/jen/TranslationsDataset/data/processed",
        help="Folder containing.jsonl files"
    )
    ap.add_argument(
        "--out-dir",
        default=str(Path("/home/jen/TranslationsDataset/data/processed") / "token_stats"),
        help="Output folder (will be created if missing)"
    )
    args = ap.parse_args()
    process_folder(args.in_dir, args.out_dir)

if __name__ == "__main__":
    main()