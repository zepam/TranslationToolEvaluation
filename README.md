# Multilingual Translation Dataset (English ↔ XX Languages)

[![Live Demo](https://img.shields.io/badge/GitHub%20Pages-Live-2ea44f?logo=github)](https://zepam.github.io/TranslationToolEvaluation/)

This dataset contains **parallel translations between English and XX world languages**, with approximately **XX sentence pairs per language**.  
It is designed to support low-resource MT research, evaluation, benchmarking, linguistics, and multilingual NLP education.

## 📦 Contents

- XX languages × XX English-source sentences each
- Cleaned and normalized text
- JSONL format and line-aligned format
- Metadata including language codes, domains, and sources
- Train/dev/test splits
- Scripts for preprocessing, combining, and generating statistics

## File Name Format

### Raw Files

`source_scenario.filetype`

ex: `portland_911_outage.csv` is a csv file containing translations about 911 outages from Portland RDPO.


### Processed Data Files

<!-- ## 🏗️ Directory Structure

See the full directory tree in the repository root. -->

<!-- ## 🔥 How to Use -->


## Project Setup

All of the code and data is in the translationsdataset package. To install the package:
`pip install -e .`

## Project Operation

### Scripts
python -m translationsdataset.scripts.convert_csv_to_json_portland

## GitHub Pages Demo

This repository includes a static demo at [demo/index.html](demo/index.html) that can be published with GitHub Pages.

1. Push to the `main` branch.
2. In repository settings, open `Pages`.
3. Set `Build and deployment` source to `GitHub Actions`.
4. The workflow at [.github/workflows/deploy-pages.yml](.github/workflows/deploy-pages.yml) will:
	- combine `data/stable/portland_*.jsonl` into `demo/alerts.json`
	- deploy the `demo` folder to GitHub Pages

Your page URL will be:
https://zepam.github.io/TranslationToolEvaluation/