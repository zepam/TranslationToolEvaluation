# USAGE:
# python tokenize_folder.py \
#   --in-dir /home/jen/TranslationsDataset/data/processed/portland \
#   --out-dir /home/jen/TranslationsDataset/data/processed/portland/token_stats


#!/usr/bin/env python3
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
    """
    Normalize placeholders {...}:
    - collapse whitespace inside braces
    - if inner contains at least one letter/number, uppercase inner
    - if empty/whitespace-only, replace with {}
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
    """Character tokens excluding whitespace, but keep {...} as a single token."""
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
    """
    Approximate multilingual tokenizer for translated alert text.
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
    """
    The initial data sources will have English as a source and not translation. Hopefully future data
    will have a different source and English as a translation. this should handle both.
    Returns a dict: lang_code -> text, with no duplicate languages per doc.

    Preference:
      - translations[lang] wins if present
      - source[lang] is used only if translations[lang] is missing

    Also maps source key 'eng' -> 'en' (common in your data).

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
    in_dir_p = Path(in_dir)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

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
        for fp, line_num, obj in iter_jsonl_records(in_dir_p):
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
    import argparse
    from pathlib import Path

    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in-dir",
        default="/home/jen/TranslationsDataset/data/processed/portland",
        help="Folder containing.jsonl files"
    )
    ap.add_argument(
        "--out-dir",
        default=str(Path("/home/jen/TranslationsDataset/data/processed/portland") / "token_stats"),
        help="Output folder (will be created if missing)"
    )
    args = ap.parse_args()
    process_folder(args.in_dir, args.out_dir)

if __name__ == "__main__":
    main()