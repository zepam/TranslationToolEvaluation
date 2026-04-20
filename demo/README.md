# Demo Folder Guide

This folder contains the browser demo(s) for exploring multilingual emergency alert translations.

## What is in this folder

- index.html
  - Main static demo entrypoint.
  - Includes a mode toggle:
    - Bundled demo data (manifest files under demo/data)
    - Local folder upload (JSONL/JSON files)
  - Uses streaming JSONL parsing and paginated rendering to reduce browser memory usage on large datasets.

- script.js
  - Legacy standalone script for an older upload-oriented page.
  - Not currently imported by index.html.

- styles.css
  - Legacy standalone style file from an earlier page variant.
  - Not currently imported by index.html.

- v1/
  - Flask-backed demo version with API endpoints and its own static frontend.
  - See v1/README.md for details.

## Running the static demo (index.html)

Use a local web server so fetch calls work correctly.

From the repository root:

python -m http.server 8000

Then open:

http://localhost:8000/demo/

### Data modes in index.html

- Bundled demo data (manifest)
  - Expects demo/data/manifest.json and referenced scenario files.
  - Good for repository-hosted demo data.

- Upload local folder (JSONL)
  - Choose a folder and click Load Folder.
  - Loader reads root-level .jsonl or .json files from the selected folder.

## Running the v1 Flask demo

See:

- v1/README.md
