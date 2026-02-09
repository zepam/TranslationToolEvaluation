# Alerts Demo (JSONL → Searchable Web UI)

- Small demo that serves newline-delimited JSON (JSONL / `.jsonl.gz`) of multilingual alerts and exposes:
  - A lightweight JSON API to list scenarios, languages, and filtered alerts.
  - A minimal single-page frontend to search and view alerts by scenario and language.
- Designed for local/demo use: it loads records into memory at startup for fast queries. It supports pointing at a single file or a directory of files.

## How to run
- Set the DATA_PATH location in `app.py`
- Start the Flask app  `python app.py`
- Open http://localhost:5000 in a browser. The UI will call /api/scenarios and /api/languages automatically.

## Project layout
- demo/
  - app.py                ← Flask backend (loads JSONL and serves API + static UI)
  - requirements.txt
  - static/
    - index.html          ← Single-page demo UI
  - data.jsonl            ← (or your files / directory; not included)

## Features
- Load a single `.jsonl`/`.jsonl.gz` file or all `.jsonl` and `.jsonl.gz` files from a directory.
- API endpoints:
  - GET `/api/scenarios` — list scenario names
  - GET `/api/languages` — list language codes present
  - GET `/api/alerts?scenario=&lang=&q=&limit=&offset=` — search/filter alerts
  - GET `/api/health` — basic health and loaded files info
  
- Frontend:
  - Scenario and language dropdowns
  - Simple substring search (English + selected translation)
  - Shows both the selected translation (if present) and the English source
  
- Transparent reading of gzipped JSONL files (`.jsonl.gz`).

## Quick install (local)
    pip install -r requirements.txt