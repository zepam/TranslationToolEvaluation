#!/usr/bin/env python3
"""
Demo API that loads JSONL (or.jsonl.gz) from a file or directory.

Set DATA_PATH environment variable to either:
- a single file: /path/to/file.jsonl
- a directory containing.jsonl /.jsonl.gz files: /path/to/dir

Endpoints:
- GET /api/scenarios
- GET /api/languages
- GET /api/alerts?scenario=&lang=&q=&limit=&offset=
- GET /api/health
- GET /              -> serves static/index.html
"""

import json
import os
import gzip
from pathlib import Path
from collections import defaultdict

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

#DATA_PATH = Path(os.environ.get("DATA_PATH", "data.jsonl"))
DATA_PATH = Path("/home/jen/TranslationsDataset/data/processed")

app = Flask(__name__, static_folder="static", static_url_path="/")
CORS(app)


def iter_lines_from_file(path: Path):
    """Yield lines from a file; transparently handle.gz files."""
    if path.suffix == ".gz":
        with gzip.open(path, "rt", encoding="utf-8") as fh:
            for line in fh:
                yield line
    else:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                yield line


def find_input_files(path: Path):
    """Return list of files to load. If path is a dir, collect *.jsonl and *.jsonl.gz."""
    if path.is_dir():
        files = sorted(path.glob("*.jsonl")) + sorted(path.glob("*.jsonl.gz"))
        return files
    elif path.exists():
        return [path]
    else:
        raise FileNotFoundError(f"DATA_PATH does not exist: {path}")


def load_jsonl(path: Path):
    records = []
    scenarios = set()
    languages = set()
    by_scenario = defaultdict(list)

    files = find_input_files(path)
    if not files:
        raise FileNotFoundError(f"No.jsonl or.jsonl.gz files found at: {path}")

    print("Loading JSONL files:")
    for f in files:
        print("  -", f)
        for i, line in enumerate(iter_lines_from_file(f)):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                print(f"Skipping malformed line in {f} (approx line {i+1}): {e}")
                continue
            records.append(obj)
            scenario = obj.get("scenario")
            if scenario:
                scenarios.add(scenario)
                by_scenario[scenario].append(len(records) - 1)
            for lang in obj.get("translations", {}).keys():
                languages.add(lang)

    return records, sorted(scenarios), sorted(languages), by_scenario, files


print("DATA_PATH:", DATA_PATH)
RECORDS, SCENARIOS, LANGUAGES, BY_SCENARIO, LOADED_FILES = load_jsonl(DATA_PATH)
print(f"Loaded {len(RECORDS)} records from {len(LOADED_FILES)} file(s). "
      f"Scenarios: {len(SCENARIOS)}, Languages: {len(LANGUAGES)}")


def pick_text(record: dict, lang: str | None) -> str:
    if lang and lang in record.get("translations", {}):
        return record["translations"][lang]
    return record.get("source", {}).get("eng", "")


@app.route("/api/scenarios")
def api_scenarios():
    return jsonify(SCENARIOS)


@app.route("/api/languages")
def api_languages():
    return jsonify(LANGUAGES)


# @app.route("/api/alerts")
# def api_alerts():
#     scenario = request.args.get("scenario")
#     lang = request.args.get("lang")
#     q = (request.args.get("q") or "").strip().lower()
#     try:
#         limit = int(request.args.get("limit", 50))
#         offset = int(request.args.get("offset", 0))
#     except ValueError:
#         return jsonify({"error": "limit and offset must be integers"}), 400

#     indices = BY_SCENARIO.get(scenario, []) if scenario else range(len(RECORDS))

#     results = []
#     for idx in indices:
#         rec = RECORDS[idx]
#         text = pick_text(rec, lang)
#         if q:
#             src = rec.get("source", {}).get("eng", "").lower()
#             trans = (text or "").lower()
#             if q not in src and q not in trans:
#                 continue
#         results.append({
#             "id": rec.get("id"),
#             "scenario": rec.get("scenario"),
#             "text": text,
#             "available_languages": sorted(rec.get("translations", {}).keys()),
#         })

#     total = len(results)
#     paged = results[offset: offset + limit]
#     return jsonify({"total": total, "offset": offset, "limit": limit, "results": paged})

@app.route("/api/alerts")
def api_alerts():
    scenario = request.args.get("scenario")
    lang = request.args.get("lang")
    q = (request.args.get("q") or "").strip().lower()
    try:
        limit = int(request.args.get("limit", 50))
        offset = int(request.args.get("offset", 0))
    except ValueError:
        return jsonify({"error": "limit and offset must be integers"}), 400

    indices = BY_SCENARIO.get(scenario, []) if scenario else range(len(RECORDS))

    results = []
    for idx in indices:
        rec = RECORDS[idx]
        english_text = rec.get("source", {}).get("eng", "")
        translations = rec.get("translations", {})
        has_translation = bool(lang and lang in translations)
        # 'text' is translation when available, otherwise English fallback
        text = translations.get(lang) if has_translation else english_text

        # filtering by q (search both English and selected text)
        if q:
            if q not in (english_text or "").lower() and q not in (text or "").lower():
                continue

        results.append({
            "id": rec.get("id"),
            "scenario": rec.get("scenario"),
            "text": text,
            "english": english_text,
            "has_translation": has_translation,
            "available_languages": sorted(translations.keys()),
        })

    total = len(results)
    paged = results[offset: offset + limit]
    return jsonify({"total": total, "offset": offset, "limit": limit, "results": paged})

@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "records": len(RECORDS),
        "loaded_files": [str(p) for p in LOADED_FILES],
    })


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(app.static_folder, filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)