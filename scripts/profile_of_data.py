#!/usr/bin/env python3
"""
compute_alert_stats.py

Usage:
    python compute_alert_stats.py --input-folder /path/to/jsons --output-dir./stats_out

Produces CSV/JSON outputs:
- per_language_stats.csv
- language_pair_stats.csv
- alignment_breakdown.csv
- domain_counts.csv
- global_summary.json

Notes:
- The script handles JSONL (one JSON object per line) and JSON files containing a list or single object.
- Adjust sentence/tokenization rules for better linguistic accuracy.
"""
import os
import json
import argparse
import re
from collections import defaultdict, Counter
import hashlib
from tqdm import tqdm
import pandas as pd

EXCLUDED_DIR_NAMES = {"stats", "tables"}

# Basic Unicode CJK detection (approx)
CJK_RE = re.compile(r'[\u4E00-\u9FFF\u3040-\u30FF\uAC00-\uD7AF]')

# Sentence splitter (lightweight): split on sentence end punctuation + line breaks.
SENT_END_RE = re.compile(r'(?<=[\.\!\?\u0964\u061F])\s+|\n+')

# Word token regex (Unicode word)
WORD_RE = re.compile(r'\w+', flags=re.UNICODE)

def read_json_objects_from_file(path):
    objs = []
    with open(path, 'r', encoding='utf-8') as fh:
        text = fh.read().strip()
        if not text:
            return objs
        # Heuristic: JSONL (many lines, each a JSON object)
        lines = text.splitlines()
        if len(lines) > 1 and all(line.strip().startswith('{') for line in lines[:5]):
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    # fallback: skip broken lines
                    continue
            return objs
        # Heuristic: single JSON array
        try:
            data = json.loads(text)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                # single object
                return [data]
        except json.JSONDecodeError:
            # fallback: try line-by-line parse
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    objs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return objs

def split_sentences(text):
    if text is None:
        return []
    text = text.strip()
    if not text:
        return []
    # If CJK characters present, fallback to treating whole text as single "sentence" if no punctuation
    if CJK_RE.search(text):
        # If punctuation present, use the same splitter; else return the whole text
        if re.search(r'[。！？\.!?]', text):
            parts = [p.strip() for p in SENT_END_RE.split(text) if p.strip()]
            return parts
        else:
            return [text]
    # Normal case: split by punctuation and newlines
    parts = [p.strip() for p in SENT_END_RE.split(text) if p.strip()]
    return parts if parts else [text]

def tokenize(text, lang_hint=None):
    if text is None:
        return []
    text = text.strip()
    if not text:
        return []
    # If CJK, fallback to character tokens (approx)
    if CJK_RE.search(text):
        # remove spaces, return list of characters excluding whitespace
        chars = [c for c in text.replace(' ', '') if not c.isspace()]
        return chars
    # Default: word regex (captures across many scripts) else whitespace split
    tokens = WORD_RE.findall(text)
    if tokens:
        return tokens
    # fallback
    return [t for t in text.split() if t]

def stable_hash_split(key, ratios=(0.8,0.1,0.1)):
    """Deterministic split by hashing key. Returns 'train'/'dev'/'test'"""
    h = hashlib.sha1(key.encode('utf-8')).hexdigest()
    v = int(h[:8], 16) / 0xFFFFFFFF
    if v < ratios[0]:
        return 'train'
    elif v < ratios[0] + ratios[1]:
        return 'dev'
    else:
        return 'test'

def process_folder(input_folder):
    # accumulators
    docs_count = 0
    languages = set()
    per_lang_doc_counts = Counter()  # number of docs where lang appears (as source or translation)
    per_lang_src_counts = Counter()  # language used as source
    per_lang_tgt_counts = Counter()  # language used as target (translation)
    per_lang_sentence_counts = Counter()
    per_lang_token_counts = Counter()
    per_lang_char_counts = Counter()
    per_lang_token_vocab = defaultdict(Counter)  # token -> count
    scenario_counts = Counter()
    pair_counts = Counter()  # (src, tgt) -> docs where pair exists
    pair_alignment_category_counts = Counter()  # (src,tgt,category) -> count
    # for more detailed pair stats:
    pair_sentence_stats = defaultdict(lambda: {'docs':0, 'total_src_sent':0, 'total_tgt_sent':0})
    per_id_lang_sent_counts = {}  # id -> {lang: num_sentences}
    ids_seen = set()

    # iterate files
    filepaths = []
    for root, dirs, files in os.walk(input_folder):
        dirs[:] = [d for d in dirs if d.lower() not in EXCLUDED_DIR_NAMES]
        for fn in files:
            if fn.lower().endswith('.json') or fn.lower().endswith('.jsonl'):
                filepaths.append(os.path.join(root, fn))
    filepaths.sort()

    # load objects
    all_objs = []
    for fp in tqdm(filepaths, desc="Reading JSON files"):
        objs = read_json_objects_from_file(fp)
        for o in objs:
            all_objs.append(o)

    # process each object (document)
    for obj in tqdm(all_objs, desc="Processing records"):
        docs_count += 1
        doc_id = obj.get('id') or obj.get('doc_id') or f"doc_{docs_count}"
        if doc_id in ids_seen:
            # handle duplicates: still process but mark unique docs only once for some stats
            pass
        ids_seen.add(doc_id)

        scenario = obj.get('scenario') or obj.get('domain') or None
        if scenario:
            scenario_counts[scenario] += 1

        # build map of language -> text for this doc
        lang_texts = {}
        # source block may be a dict of languages
        src_block = obj.get('source') or {}
        if isinstance(src_block, dict):
            for lang, txt in src_block.items():
                if txt is not None:
                    lang_texts[lang] = txt
        elif isinstance(src_block, str):
            # assume english? but keep under key 'source'
            lang_texts['source'] = src_block

        trans_block = obj.get('translations') or {}
        if isinstance(trans_block, dict):
            for lang, txt in trans_block.items():
                if txt is not None:
                    lang_texts[lang] = txt
        # now we have combined set of language texts for this doc
        # update per-lang doc counts (count doc if language appears here)
        for lang in lang_texts.keys():
            languages.add(lang)
            per_lang_doc_counts[lang] += 1

        # count src/tgt separately
        if isinstance(src_block, dict):
            for lang in src_block.keys():
                per_lang_src_counts[lang] += 1
        elif isinstance(src_block, str):
            per_lang_src_counts['source'] += 1

        if isinstance(trans_block, dict):
            for lang in trans_block.keys():
                per_lang_tgt_counts[lang] += 1

        # For alignment and sentence metrics: iterate each src lang and each target lang
        # Compute sentence/token/char counts per language
        this_doc_lang_sent_counts = {}
        for lang, txt in lang_texts.items():
            sents = split_sentences(txt)
            num_sents = len(sents)
            this_doc_lang_sent_counts[lang] = num_sents
            per_lang_sentence_counts[lang] += num_sents
            # tokens and chars
            tok_count = 0
            char_count = 0
            for s in sents:
                toks = tokenize(s, lang_hint=lang)
                tok_count += len(toks)
                char_count += len(s)
                # accumulate vocab counts
                for t in toks:
                    # normalize tokens for Latin scripts heuristically
                    per_lang_token_vocab[lang][t.lower()] += 1
            per_lang_token_counts[lang] += tok_count
            per_lang_char_counts[lang] += char_count

        per_id_lang_sent_counts[doc_id] = this_doc_lang_sent_counts

        # pairwise stats: for each source lang (in source block) and each target lang (in translations)
        src_langs = list(src_block.keys()) if isinstance(src_block, dict) else (['source'] if isinstance(src_block, str) else [])
        tgt_langs = list(trans_block.keys()) if isinstance(trans_block, dict) else []
        for s in src_langs:
            for t in tgt_langs:
                pair_counts[(s,t)] += 1
                # alignment category by sentences
                s_sents = this_doc_lang_sent_counts.get(s, 0)
                t_sents = this_doc_lang_sent_counts.get(t, 0)
                # classify
                if s_sents == 1 and t_sents == 1:
                    cat = '1:1'
                elif s_sents == 1 and t_sents > 1:
                    cat = '1:n'
                elif s_sents > 1 and t_sents == 1:
                    cat = 'n:1'
                elif s_sents == 0 and t_sents == 0:
                    cat = '0:0'
                else:
                    cat = 'n:m'  # includes >1:>1 and mixed cases
                pair_alignment_category_counts[(s,t,cat)] += 1
                pair_sentence_stats[(s,t)]['docs'] += 1
                pair_sentence_stats[(s,t)]['total_src_sent'] += s_sents
                pair_sentence_stats[(s,t)]['total_tgt_sent'] += t_sents

    # Build per-language DataFrame
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

    # Pairwise stats DataFrame
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

    # Alignment breakdown: convert pair_alignment_category_counts to table
    align_rows = []
    for (s,t,cat), cnt in pair_alignment_category_counts.items():
        align_rows.append({'src':s,'tgt':t,'category':cat,'count':cnt})
    align_df = pd.DataFrame(align_rows).pivot_table(index=['src','tgt'], columns='category', values='count', fill_value=0)
    align_df = align_df.reset_index()

    # Domain/scenario counts
    domain_df = pd.DataFrame([{'scenario':k,'count':v} for k,v in scenario_counts.items()]).sort_values('count', ascending=False)

    # Global summary
    total_docs = docs_count
    total_sentences = sum(per_lang_sentence_counts.values())  # note: double counts if same sentence appears in multiple languages
    total_tokens = sum(per_lang_token_counts.values())
    global_summary = {
        'total_docs': total_docs,
        'languages': sorted(list(languages)),
        'num_languages': len(languages),
        'total_sentences_approx': int(total_sentences),
        'total_tokens_approx': int(total_tokens),
        'total_pairs': len(pair_counts),
    }

    # Translation coverage: percent of docs having translation into each language (relative to total_docs)
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

def generate_data_profile(jsonl_folder):
    results = process_folder(jsonl_folder)
    save_outputs(results, os.path.join(jsonl_folder, 'stats'))


def main(processed_filepath=None):
    # ap = argparse.ArgumentParser()
    # ap.add_argument('--input-folder', required=True, help='Folder containing JSON/JSONL files')
    # ap.add_argument('--output-dir', default='./stats_out', help='Output directory for CSV/JSON results')
    # args = ap.parse_args()


    # input_folder = '/home/jen/TranslationsDataset/data/processed/portland'
    # output_dir = '/home/jen/TranslationsDataset/data/processed/portland/stats'
    # results = process_folder(input_folder)
    # save_outputs(results, output_dir)

    if processed_filepath is None:
        print("No jsonl_folder provided. Please provide the path to the folder containing the JSONL files.")
    generate_data_profile(processed_filepath)
    

if __name__ == '__main__':
    main()