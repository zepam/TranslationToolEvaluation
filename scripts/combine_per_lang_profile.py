#!/usr/bin/env python3
"""Language profile analyzer for multilingual alert dataset.

This module processes JSONL files containing multilingual alert data and generates
per-language statistics including document counts, token counts, vocabulary size,
and average sentence metrics. Supports CJK languages and character-based tokenization.

Key features:
    - Loads language code mappings from Python files
    - Normalizes and tokenizes text with language-specific handling
    - Deduplicates documents by ID
    - Generates per-language statistical profiles
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional, Iterable
import pandas as pd
import regex as re
import importlib.util

# -----------------------
# Import language codes
# -----------------------
def load_code_to_name_from_py(py_path: str, var_name: str = "langauge_codes") -> dict:
    """Load language code mappings from a Python file.
    
    Imports a Python module containing a dictionary of language definitions and
    converts it to a code->name mapping. Prioritizes ISO 639-1 codes, falls back
    to ISO 639-2 if ISO 639-1 is unavailable.
    
    Args:
        py_path (str): Path to the Python file containing the language codes dictionary.
        var_name (str): Name of the dictionary variable in the Python file.
            Defaults to "langauge_codes".
    
    Returns:
        dict: Dictionary mapping language codes (e.g., 'am', 'ar') to language names
            (e.g., 'Amharic', 'Arabic'). Only includes languages with valid codes.
    """
    py_path = str(Path(py_path))

    spec = importlib.util.spec_from_file_location("language_codes_module", py_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)

    data = getattr(module, var_name)

    code_to_name = {}
    for lang_name, codes in data.items():
        if not isinstance(codes, dict):
            continue
        code = codes.get("iso639-1") or codes.get("iso639-2")
        if code:
            code_to_name[str(code)] = lang_name
    return code_to_name

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
# Sentence splitting
# -----------------------
SENT_END_RE = re.compile(r'(?<=[\.\!\?\u0964\u061F\u3002\uFF01\uFF1F])\s+|\n+')

def split_sentences(text: str) -> List[str]:
    """Split text into sentences using multilingual punctuation markers.
    
    Splits on common sentence delimiters including periods, exclamation marks,
    question marks, and their Unicode equivalents in various scripts (Devanagari,
    Arabic, CJK, etc.). Whitespace variations are handled consistently.
    
    Args:
        text (str | None): Text to split into sentences.
    
    Returns:
        list[str]: List of sentences, stripped of whitespace. Returns empty list
            for None or empty input.
    """
    if text is None:
        return []
    t = text.strip()
    if not t:
        return []
    parts = [p.strip() for p in SENT_END_RE.split(t) if p.strip()]
    return parts if parts else [t]

# -----------------------
# Tokenization
# -----------------------
CJK_RE = re.compile(r'[\p{Script=Han}\p{Script=Hiragana}\p{Script=Katakana}\p{Script=Hangul}]')
WORDLIKE_OR_PLACEHOLDER_RE = re.compile(r"\{[^{}]+\}|[\p{L}\p{M}]+|\p{N}+", flags=re.UNICODE)

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

    if CJK_RE.search(t) or (primary in {"zh", "ja", "ko"}):
        return _char_tokens_keep_placeholders(t)

    if primary in {"th", "lo", "km", "my"}:
        return _char_tokens_keep_placeholders(t)

    return WORDLIKE_OR_PLACEHOLDER_RE.findall(t)

# -----------------------
# No double-counting across source/translations
# -----------------------
def build_doc_texts(obj: Dict[str, Any]) -> Dict[str, str]:
    """Extract language->text mappings from an alert document.
    
    Builds a deduplicated mapping of language codes to text content. Translations
    take priority over source text. English source language code 'eng' is normalized
    to 'en'. Skips None or empty values.
    
    Args:
        obj (dict): Alert document with optional 'translations' and 'source' fields,
            each containing language code -> text mappings.
    
    Returns:
        dict: Mapping of normalized language codes to text strings. At most one
            text per language (translations preferred over source).
    """
    texts: Dict[str, str] = {}

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
            if lang_norm not in texts:
                texts[lang_norm] = txt

    return texts

# -----------------------
# Folder reading (non-recursive)
# -----------------------
EXCLUDED_DIR_NAMES = {"stats", "tables"}


def iter_source_dirs(in_dir: Path) -> List[Path]:
    """Return source directories to process.

    If in_dir is the processed root, returns immediate child directories except
    excluded folders such as stats and tables. If in_dir already points to a
    source directory, returns that directory only.
    """
    if not in_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {in_dir}")

    child_source_dirs = [
        p for p in sorted(in_dir.iterdir())
        if p.is_dir() and p.name.lower() not in EXCLUDED_DIR_NAMES
    ]
    if child_source_dirs:
        return child_source_dirs
    return [in_dir]


def iter_json_objects(in_dir: Path) -> Iterable[Dict[str, Any]]:
    """Iterate through JSON objects from top-level JSON/JSONL files.

    Only reads files directly inside each source folder (non-recursive), and
    intentionally skips stats/tables subfolders by not descending into them.
    """
    source_dirs = iter_source_dirs(in_dir)

    for source_dir in source_dirs:
        json_files = [
            fp for fp in sorted(source_dir.iterdir())
            if fp.is_file() and fp.suffix.lower() in {".json", ".jsonl"}
        ]

        for fp in json_files:
            # Skip aggregate profile files; this profiler expects per-alert records.
            if fp.name.endswith("_data_profile.json"):
                continue

            if fp.suffix.lower() == ".jsonl":
                with fp.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            yield json.loads(line)
                        except json.JSONDecodeError:
                            continue
            else:
                with fp.open("r", encoding="utf-8") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        continue

                if isinstance(data, list):
                    for obj in data:
                        if isinstance(obj, dict):
                            yield obj
                elif isinstance(data, dict):
                    yield data

# -----------------------
# Main profiling
# -----------------------
def profile_languages(in_dir: str, out_csv: str, lang_code_to_name: Dict[str, str], dedupe_ids: bool = True):
    """Generate per-language statistics from JSONL alert documents.
    
    Processes all JSONL files in a directory and computes per-language statistics:
    document count, sentence count, token count, character count, vocabulary size,
    and derived metrics (avg tokens/sentence, avg chars/sentence). Results are
    saved to CSV sorted by token count (descending).
    
    Args:
        in_dir (str): Directory containing JSONL files to process.
        out_csv (str): Path to output CSV file. Parent directories are created
            if they don't exist.
        lang_code_to_name (dict): Mapping of language codes to human-readable
            language names.
        dedupe_ids (bool): If True, skips documents with duplicate IDs (default True).
    
    Returns:
        None. Writes CSV file and prints confirmation message.
    """
    in_dir_p = Path(in_dir)
    ids_seen = set()

    docs = Counter()
    sentences = Counter()
    tokens = Counter()
    chars = Counter()
    vocab = defaultdict(set)  # lang -> set of tokens (lowercased)

    for obj in iter_json_objects(in_dir_p):
        doc_id = obj.get("id")
        if dedupe_ids and doc_id is not None:
            if doc_id in ids_seen:
                continue
            ids_seen.add(doc_id)

        texts = build_doc_texts(obj)
        for lang_code, text in texts.items():
            docs[lang_code] += 1

            text_norm = normalize_placeholders(text)
            chars[lang_code] += len(text_norm)

            sents = split_sentences(text_norm)
            sentences[lang_code] += len(sents)

            for s in sents:
                toks = tokenize_translation(s, lang_code=lang_code)
                tokens[lang_code] += len(toks)
                for t in toks:
                    vocab[lang_code].add(t.lower())

    rows = []
    for lang_code in sorted(docs.keys()):
        #TODO using two character lang codes, merges Chinese and skips Marshallese and Karen. Consider using the original lang codes from the data instead of mapping to ISO 639-1, or at least preserve the original code in the output.
        lang_name = lang_code_to_name.get(lang_code, lang_code)

        d = docs[lang_code]
        s = sentences[lang_code]
        t = tokens[lang_code]
        c = chars[lang_code]

        rows.append({
            "Language Name": lang_name,
            "Lang Code": lang_code,
            "Num of Docs": d,
            "Num of Sentences": s,
            "Num of Tokens": t,
            "Num of Characters": c,
            "Avg Tokens per Sentence": round(t / s, 3) if s else 0.0,
            "Avg Characters per Sentence": round(c / s, 3) if s else 0.0,
            "Vocabulary Size": len(vocab[lang_code]),
        })

    df = pd.DataFrame(rows).sort_values(["Num of Tokens"], ascending=False)
    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Wrote: {out_csv}")

def main():
    """Command-line interface for language profiling.
    
    Parses arguments and runs the language profiling pipeline on JSONL files
    from the specified directory.
    
    Command-line arguments:
        --in-dir: Directory containing .jsonl files (default: processed/portland).
        --out-csv: Output CSV path (default: processed/portland/stats/per_language_profile.csv).
        --no-dedupe: If set, do not deduplicate documents by ID.
        --lang-map: Path to language code mapping file (default: language_codes.py).
    """
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in-dir",
        default="/home/jen/TranslationsDataset/data/processed",
        help=(
            "Either data/processed root (uses source folders only, excluding stats/tables) "
            "or a specific source folder under data/processed"
        ),
    )
    ap.add_argument(
        "--out-csv",
        default="/home/jen/TranslationsDataset/data/processed/stats/combined_per_language_profile.csv",
        help="Output CSV",
    )
    ap.add_argument("--no-dedupe", action="store_true", help="Do not dedupe by id")
    ap.add_argument("--lang-map", default="/home/jen/TranslationsDataset/data/language_codes.py",
                    help="Path to your language mapping JSON (from your lang_code file)")
    args = ap.parse_args()

    code_to_name = load_code_to_name_from_py(
        "/home/jen/TranslationsDataset/data/language_codes.py",
        var_name="language_codes"
    )

    profile_languages(
        args.in_dir, 
        args.out_csv, 
        lang_code_to_name=code_to_name, 
        dedupe_ids=not args.no_dedupe
    )

if __name__ == "__main__":
    main()