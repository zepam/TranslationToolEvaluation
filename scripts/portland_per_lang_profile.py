#!/usr/bin/env python3
import json
from pathlib import Path
from collections import Counter, defaultdict
from typing import Dict, Any, List, Optional
import pandas as pd
import regex as re
import importlib.util

# -----------------------
# Import language codes
# -----------------------
def load_code_to_name_from_py(py_path: str, var_name: str = "langauge_codes") -> dict:
    """
    Loads a Python file containing a dict called `langauge_codes`:
      langauge_codes = {"Amharic": {"iso639-2": "amh", "iso639-1": "am"},...}

    Returns: { "am": "Amharic", "ar": "Arabic",... }
    Prefers iso639-1, falls back to iso639-2.
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
    """
    Returns lang_code -> text with at most one text per language per doc.
    Preference: translations wins; source fills gaps.
    Maps source 'eng' -> 'en'.
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
def iter_jsonl_objects(in_dir: Path):
    for fp in sorted(in_dir.glob("*.jsonl")):  # NOT recursive
        with fp.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    continue

# -----------------------
# Main profiling
# -----------------------
def profile_languages(in_dir: str, out_csv: str, lang_code_to_name: Dict[str, str], dedupe_ids: bool = True):
    in_dir_p = Path(in_dir)
    ids_seen = set()

    docs = Counter()
    sentences = Counter()
    tokens = Counter()
    chars = Counter()
    vocab = defaultdict(set)  # lang -> set of tokens (lowercased)

    for obj in iter_jsonl_objects(in_dir_p):
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
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--in-dir", default="/home/jen/TranslationsDataset/data/processed/portland", help="Directory containing .jsonl files (non-recursive)")
    ap.add_argument("--out-csv", default="/home/jen/TranslationsDataset/data/processed/portland/stats/per_language_profile.csv", help="Output CSV")
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