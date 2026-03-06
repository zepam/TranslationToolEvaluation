#!/usr/bin/env python3
"""
compute_alert_stats_tokenized.py

Usage:
    python compute_alert_stats_tokenized.py --input-folder /path/to/jsons --output-dir./stats_out \
       [--download-stanza] [--stanza-langs en,es,fr,...]

Produces CSV/JSON outputs:
- per_language_stats.csv
- language_pair_stats.csv
- alignment_breakdown.csv
- domain_counts.csv
- translation_coverage.csv
- global_summary.json

Notes:
- The script will try to use Stanza (and other language-specific tokenizers) if installed.
- Use --download-stanza to download Stanza models for requested languages.
"""
import os
import json
import argparse
import re
from collections import defaultdict, Counter
import hashlib
from tqdm import tqdm
import pandas as pd
#TODO convert language map to json for easier import
# OPTIONAL imports; we handle missing packages gracefully
# try:
#     import stanza
# except Exception:
#     stanza = None

# try:
#     import jieba
# except Exception:
#     jieba = None

# try:
#     from pythainlp import word_tokenize as thai_word_tokenize
# except Exception:
#     thai_word_tokenize = None

# try:
#     from fugashi import Tagger as FugashiTagger

# except Exception:
#     FugashiTagger = None

# -------------------------
# Tokenizer / Sentence Splitter Factory
# -------------------------
PLACEHOLDER_RE = re.compile(r'\{[^}]+\}')
CJK_RE = re.compile(r'[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]')

# Dataset language mapping: dataset language codes -> stanza/lang codes (edit as needed)

# LANG_CODE_MAP = {
#     'eng': 'en', 'spa': 'es', 'fra': 'fr', 'ara': 'ar', 'rus': 'ru', 'ukr': 'uk',
#     'hin': 'hi', 'nep': 'ne', 'jpn': 'ja', 'kor': 'ko', 'chi': 'zh', 'vie': 'vi',
#     'tha': 'th', 'khm': 'km', 'lao': 'lo', 'bur': 'my', 'amh': 'am', 'ron': 'ro',
#     'swa': 'sw', 'som': 'so', 'tgl': 'tl', 'chk': 'chk'  # 'chk' likely unsupported
# }

LANG_CODE_MAP = {
    "Amharic": "amh",
    "Arabic": "ara",
    "Burmese": "bur",
    "Chuukese": "chk",
    "English": "eng",
    "Persian/Farsi": "fas",  # originally persian/farsi
    "French": "fra",
    "Hindi": "hin",
    "Hmong": "hmn",
    "Japanese": "jpn",
    "Karen": "kar",
    "Khmer": "khm",
    "Korean": "kor",
    "Lao": "lao",
    "Marshallese": "mah",
    "Mien": "ium",        # Iu Mien
    "Nepali": "nep",        # nepali macrolanguage
    "Oromo": "orm",
    "Pashto": "pus",        # pashto/pushto macrolanguage
    "Romanian": "ron",
    "Rohingya": "rhg",
    "Russian": "rus",
    "Serbian": "srp",
    "Simplified Chinese": "zh-Hans", #check to see which is being used
    "Somali": "som",
    "Spanish": "spa",
    "Swahili": "swa",
    "Tagalog": "tgl",
    "Telugu": "tel",
    "Thai": "tha",
    "Traditional Chinese": "zh-Hant", #check to see which is being used
    "Ukrainian": "ukr",
    "Vietnamese": "vie",
}

# Which languages we consider for Stanza by default (common languages)
# DEFAULT_STANZA_LANGS = set([
#     'eng','spa','fra','ara','rus','ukr','hin','nep','jpn','kor','zh','vie','tha','khm','lao','bur','amh','ron','swa','som','tgl'
# ])

# caches
_pipeline_cache = {}
# _fugashi_tagger = None

def protect_placeholders(text):
    """Replace {name} with sentinel tokens so tokenizers don't break them."""
    def repl(m):
        inner = m.group(0)[1:-1]
        return f"<<<PH:{inner}>>>"
    return PLACEHOLDER_RE.sub(repl, text)

def unprotect_placeholders_in_tokens(tokens):
    restored = []
    for t in tokens:
        if t.startswith("<<<PH:") and t.endswith(">>>"):
            name = t[6:-3]
            restored.append("{" + name + "}")
        else:
            restored.append(t)
    return restored

def unprotect_placeholders_in_text(text):
    return re.sub(r'<<<PH:([^>]+)>>>', lambda m: "{" + m.group(1) + "}", text)

def ensure_stanza_pipeline(lang, download_if_missing=False):
    """Return a stanza Pipeline for lang (tokenize only)."""
    if stanza is None:
        raise RuntimeError("Stanza is not installed")
    if lang in _pipeline_cache:
        return _pipeline_cache[lang]
    # try to create pipeline; download model if requested
    try:
        nlp = stanza.Pipeline(lang=lang, processors='tokenize', tokenize_pretokenized=False, verbose=False)
        _pipeline_cache[lang] = nlp
        return nlp
    except Exception:
        if download_if_missing:
            try:
                stanza.download(lang, verbose=False)
                nlp = stanza.Pipeline(lang=lang, processors='tokenize', tokenize_pretokenized=False, verbose=False)
                _pipeline_cache[lang] = nlp
                return nlp
            except Exception as e:
                raise RuntimeError(f"Failed to download or init stanza model for {lang}: {e}")
        else:
            raise

def stanza_tokenize_and_split(text, lang, download_if_missing=False):
    nlp = ensure_stanza_pipeline(lang, download_if_missing=download_if_missing)
    doc = nlp(text)
    sents = []
    toks_per_sent = []
    for s in doc.sentences:
        sents.append(s.text.strip())
        toks_per_sent.append([t.text for t in s.tokens])
    return sents, toks_per_sent

def fugashi_tokenize_and_split(text):
    global _fugashi_tagger
    if FugashiTagger is None:
        raise RuntimeError("fugashi not installed")
    if _fugashi_tagger is None:
        _fugashi_tagger = FugashiTagger()
    toks = [m.surface for m in _fugashi_tagger(text)]
    # naive sentence segmentation
    sents = [text.strip()] if text.strip() else []
    return sents, [toks]

def jieba_tokenize_and_split(text):
    if jieba is None:
        raise RuntimeError("jieba not installed")
    toks = list(jieba.cut(text))
    # sentence split by Chinese/Japanese punctuation
    sents = [s.strip() for s in re.split(r'(?<=[。！？\.\!\?])\s+', text) if s.strip()]
    toks_per_sent = []
    if sents:
        for s in sents:
            toks_per_sent.append(list(jieba.cut(s)))
    else:
        toks_per_sent = [toks]
    return sents if sents else [text], toks_per_sent

def thai_tokenize_and_split(text):
    if thai_word_tokenize is None:
        raise RuntimeError("pythainlp not installed")
    toks = thai_word_tokenize(text, engine='newmm')
    sents = [s.strip() for s in re.split(r'(?<=[\.\!\?\n])\s+', text) if s.strip()]
    if sents:
        toks_per_sent = [thai_word_tokenize(s, engine='newmm') for s in sents]
    else:
        toks_per_sent = [toks]
    return sents if sents else [text], toks_per_sent

def regex_tokenize_and_split(text):
    # Token regex preserves placeholders sentinels e.g., <<<PH:name>>>
    TOK_RE = re.compile(r'<<<PH:[^>]+>>>|\w+|[^\s\w]', flags=re.UNICODE)
    sents = [s.strip() for s in re.split(r'(?<=[\.\!\?\n])\s+', text) if s.strip()]
    if sents:
        toks_per_sent = [TOK_RE.findall(s) for s in sents]
    else:
        toks_per_sent = [TOK_RE.findall(text)]
        sents = [text]
    return sents, toks_per_sent

def get_tokenizer_for_dataset_lang(dataset_lang_code, download_stanza=False):
    """
    Returns a function tokenize_and_split(text) -> (sentences_list, tokens_per_sentence_list)
    dataset_lang_code is e.g., 'eng', 'spa', 'jpn', etc.
    """
    lang = LANG_CODE_MAP.get(dataset_lang_code, dataset_lang_code)

    def tokenize_and_split(text):
        if text is None:
            return [], []
        text_prot = protect_placeholders(text)
        # prefer language-specific tokenizers where available
        try:
            # Japanese prefer fugashi if installed
            if lang == 'jpn' and FugashiTagger is not None:
                sents, toks = fugashi_tokenize_and_split(text_prot)
            # Chinese prefer jieba if installed
            elif lang in ('zh', 'chi', 'zh-Hans', 'zh-Hant') and jieba is not None:
                sents, toks = jieba_tokenize_and_split(text_prot)
            # Thai prefer pythainlp
            elif lang == 'th' and thai_word_tokenize is not None:
                sents, toks = thai_tokenize_and_split(text_prot)
            # Try stanza for languages in the default list (or any lang if stanza present)
            elif stanza is not None:
                # Try stanza, optionally download if missing
                try:
                    sents, toks = stanza_tokenize_and_split(text_prot, lang, download_if_missing=download_stanza)
                except Exception:
                    # fallback to regex
                    sents, toks = regex_tokenize_and_split(text_prot)
            else:
                # fallback
                sents, toks = regex_tokenize_and_split(text_prot)
        except Exception:
            # ensure robust fallback
            sents, toks = regex_tokenize_and_split(text_prot)

        # restore placeholders in sentence text and tokens
        sents = [unprotect_placeholders_in_text(s) for s in sents]
        toks = [unprotect_placeholders_in_tokens(tlist) for tlist in toks]

        # print the language and tokenizer used 
        print(f"language '{dataset_lang_code}' (mapped to '{lang}') using tokenizer: {'fugashi' if (lang == 'ja' and FugashiTagger is not None) else 'jieba' if (lang in ('zh', 'chi') and jieba is not None) else 'stanza' if stanza is not None else 'regex fallback'}")


        return sents, toks

    return tokenize_and_split

# -------------------------
# JSON reading & stats logic
# -------------------------
def read_json_objects_from_file(path):
    objs = []
    with open(path, 'r', encoding='utf-8') as fh:
        text = fh.read().strip()
        if not text:
            return objs
        lines = text.splitlines()
        if len(lines) > 1 and all(line.strip().startswith('{') for line in lines[:5]):
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
            return objs
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return [data]
        except json.JSONDecodeError:
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return objs

def stable_hash_split(key, ratios=(0.8,0.1,0.1)):
    h = hashlib.sha1(key.encode('utf-8')).hexdigest()
    v = int(h[:8], 16) / 0xFFFFFFFF
    if v < ratios[0]:
        return 'train'
    elif v < ratios[0] + ratios[1]:
        return 'dev'
    else:
        return 'test'

def process_folder(input_folder, download_stanza=False, stanza_langs=None):
    # Accumulators
    docs_count = 0
    languages = set()
    per_lang_doc_counts = Counter()
    per_lang_src_counts = Counter()
    per_lang_tgt_counts = Counter()
    per_lang_sentence_counts = Counter()
    per_lang_token_counts = Counter()
    per_lang_char_counts = Counter()
    per_lang_token_vocab = defaultdict(Counter)
    scenario_counts = Counter()
    pair_counts = Counter()
    pair_alignment_category_counts = Counter()
    pair_sentence_stats = defaultdict(lambda: {'docs':0, 'total_src_sent':0, 'total_tgt_sent':0})
    per_id_lang_sent_counts = {}
    ids_seen = set()

    # Build tokenizer cache for dataset languages encountered
    tokenizer_cache = {}

    # collect files
    filepaths = []
    for root, _, files in os.walk(input_folder):
        for fn in files:
            if fn.lower().endswith('.json') or fn.lower().endswith('.jsonl'):
                filepaths.append(os.path.join(root, fn))
    filepaths.sort()

    # read all objects
    all_objs = []
    for fp in tqdm(filepaths, desc="Reading JSON files"):
        objs = read_json_objects_from_file(fp)
        for o in objs:
            all_objs.append(o)

    # process each record
    for obj in tqdm(all_objs, desc="Processing records"):
        docs_count += 1
        doc_id = obj.get('id') or obj.get('doc_id') or f"doc_{docs_count}"
        if doc_id in ids_seen:
            pass
        ids_seen.add(doc_id)

        scenario = obj.get('scenario') or obj.get('domain') or None
        if scenario:
            scenario_counts[scenario] += 1

        # build map of language -> text
        lang_texts = {}
        src_block = obj.get('source') or {}
        if isinstance(src_block, dict):
            for lang, txt in src_block.items():
                if txt is not None:
                    lang_texts[lang] = txt
        elif isinstance(src_block, str):
            lang_texts['source'] = src_block

        trans_block = obj.get('translations') or {}
        if isinstance(trans_block, dict):
            for lang, txt in trans_block.items():
                if txt is not None:
                    lang_texts[lang] = txt

        # update doc counts
        for lang in lang_texts.keys():
            languages.add(lang)
            per_lang_doc_counts[lang] += 1

        if isinstance(src_block, dict):
            for lang in src_block.keys():
                per_lang_src_counts[lang] += 1
        elif isinstance(src_block, str):
            per_lang_src_counts['source'] += 1

        if isinstance(trans_block, dict):
            for lang in trans_block.keys():
                per_lang_tgt_counts[lang] += 1

        # tokenize and count per language in this doc
        this_doc_lang_sent_counts = {}
        for lang, txt in lang_texts.items():
            # get tokenizer
            if lang not in tokenizer_cache:
                # if user supplied a stanza_langs list, only download those when requested
                tokenizer_cache[lang] = get_tokenizer_for_dataset_lang(lang, download_stanza=(download_stanza and (stanza_langs is None or LANG_CODE_MAP.get(lang, lang) in stanza_langs)))
            tokfn = tokenizer_cache[lang]
            sents, toks_per_sent = tokfn(txt)
            num_sents = len(sents)
            this_doc_lang_sent_counts[lang] = num_sents
            per_lang_sentence_counts[lang] += num_sents
            tok_count = sum(len(toks) for toks in toks_per_sent)
            char_count = sum(len(s) for s in sents)
            per_lang_token_counts[lang] += tok_count
            per_lang_char_counts[lang] += char_count
            for toks in toks_per_sent:
                for t in toks:
                    per_lang_token_vocab[lang][t] += 1

        per_id_lang_sent_counts[doc_id] = this_doc_lang_sent_counts

        # pairwise stats
        src_langs = list(src_block.keys()) if isinstance(src_block, dict) else (['source'] if isinstance(src_block, str) else [])
        tgt_langs = list(trans_block.keys()) if isinstance(trans_block, dict) else []
        for s in src_langs:
            for t in tgt_langs:
                pair_counts[(s,t)] += 1
                s_sents = this_doc_lang_sent_counts.get(s, 0)
                t_sents = this_doc_lang_sent_counts.get(t, 0)
                if s_sents == 1 and t_sents == 1:
                    cat = '1:1'
                elif s_sents == 1 and t_sents > 1:
                    cat = '1:n'
                elif s_sents > 1 and t_sents == 1:
                    cat = 'n:1'
                elif s_sents == 0 and t_sents == 0:
                    cat = '0:0'
                else:
                    cat = 'n:m'
                pair_alignment_category_counts[(s,t,cat)] += 1
                pair_sentence_stats[(s,t)]['docs'] += 1
                pair_sentence_stats[(s,t)]['total_src_sent'] += s_sents
                pair_sentence_stats[(s,t)]['total_tgt_sent'] += t_sents

    # Build outputs
    rows = []
    for lang in sorted(languages):
        docs = per_lang_doc_counts.get(lang, 0)
        srcc = per_lang_src_counts.get(lang, 0)
        tgtc = per_lang_tgt_counts.get(lang, 0)
        sents = per_lang_sentence_counts.get(lang, 0)
        toks = per_lang_token_counts.get(lang, 0)
        chars = per_lang_char_counts.get(lang, 0)
        avg_sent_tokens = (toks / sents) if sents else 0
        avg_sent_chars = (chars / sents) if sents else 0
        vocab_size = len(per_lang_token_vocab[lang])
        rows.append({
            'language': lang,
            'docs': docs,
            'as_source_count': srcc,
            'as_target_count': tgtc,
            'sentences': sents,
            'tokens': toks,
            'chars': chars,
            'avg_sentence_tokens': round(avg_sent_tokens,2),
            'avg_sentence_chars': round(avg_sent_chars,2),
            'vocab_size': vocab_size
        })
    per_lang_df = pd.DataFrame(rows).sort_values(['tokens'], ascending=False)

    pair_rows = []
    for (s,t), cnt in pair_counts.items():
        stats = pair_sentence_stats[(s,t)]
        docs = stats['docs']
        avg_src_sent = stats['total_src_sent'] / docs if docs else 0
        avg_tgt_sent = stats['total_tgt_sent'] / docs if docs else 0
        pair_rows.append({
            'src': s,
            'tgt': t,
            'docs_with_pair': cnt,
            'avg_src_sentences': round(avg_src_sent,2),
            'avg_tgt_sentences': round(avg_tgt_sent,2)
        })
    pair_df = pd.DataFrame(pair_rows).sort_values(['docs_with_pair'], ascending=False)

    # Alignment breakdown pivot
    align_rows = []
    for (s,t,cat), cnt in pair_alignment_category_counts.items():
        align_rows.append({'src':s,'tgt':t,'category':cat,'count':cnt})
    if align_rows:
        align_df = pd.DataFrame(align_rows).pivot_table(index=['src','tgt'], columns='category', values='count', fill_value=0).reset_index()
    else:
        align_df = pd.DataFrame(columns=['src','tgt','1:1','1:n','n:1','n:m','0:0'])

    domain_df = pd.DataFrame([{'scenario':k,'count':v} for k,v in scenario_counts.items()]).sort_values('count', ascending=False)

    total_docs = docs_count
    total_sentences = sum(per_lang_sentence_counts.values())
    total_tokens = sum(per_lang_token_counts.values())
    global_summary = {
        'total_docs': total_docs,
        'languages': sorted(list(languages)),
        'num_languages': len(languages),
        'total_sentences_approx': int(total_sentences),
        'total_tokens_approx': int(total_tokens),
        'E-X_translation_total_pairs': len(pair_counts),
    }

    coverage_rows = []
    for lang in sorted(languages):
        translated_count = per_lang_tgt_counts.get(lang, 0)
        coverage = 100.0 * translated_count / total_docs if total_docs else 0.0
        coverage_rows.append({'language':lang,'translated_docs': translated_count,'coverage_percent': round(coverage,2)})
    coverage_df = pd.DataFrame(coverage_rows).sort_values('coverage_percent', ascending=False)

    return {
        'per_lang_df': per_lang_df,
        'pair_df': pair_df,
        'align_df': align_df,
        'domain_df': domain_df,
        'coverage_df': coverage_df,
        'global_summary': global_summary
    }

def save_outputs(results, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    results['per_lang_df'].to_csv(os.path.join(out_dir, 'per_language_stats.csv'), index=False)
    results['pair_df'].to_csv(os.path.join(out_dir, 'language_pair_stats.csv'), index=False)
    results['align_df'].to_csv(os.path.join(out_dir, 'alignment_breakdown.csv'), index=False)
    results['domain_df'].to_csv(os.path.join(out_dir, 'domain_counts.csv'), index=False)
    results['coverage_df'].to_csv(os.path.join(out_dir, 'translation_coverage.csv'), index=False)
    with open(os.path.join(out_dir, 'global_summary.json'), 'w', encoding='utf-8') as fh:
        json.dump(results['global_summary'], fh, ensure_ascii=False, indent=2)
    print("Wrote outputs to", out_dir)

def parse_stanza_langs(arg):
    if not arg:
        return None
    return set([a.strip() for a in arg.split(',') if a.strip()])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input-folder', help='Folder containing JSON/JSONL files', default='/home/jen/TranslationsDataset/data/processed/portland')
    ap.add_argument('--output-dir', default='/home/jen/TranslationsDataset/data/processed/portland/stats_out', help='Output directory for CSV/JSON results')
    ap.add_argument('--download-stanza', action='store_true', help='If set, download stanza models for requested languages (may be large)')
    ap.add_argument('--stanza-langs', default=None, help='Comma-separated stanza lang codes to download/use (e.g., en,es,fr). If omitted, uses defaults where possible.')
    args = ap.parse_args()

    stanza_langs = parse_stanza_langs(args.stanza_langs) if args.stanza_langs else None
    if args.download_stanza and stanza is None:
        print("Warning: --download-stanza requested but stanza is not installed. Install stanza to use this feature.")

    results = process_folder(args.input_folder, download_stanza=args.download_stanza, stanza_langs=stanza_langs)
    save_outputs(results, args.output_dir)

if __name__ == '__main__':
    main()