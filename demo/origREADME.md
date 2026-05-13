# Multilingual Translation Dataset (English ↔ XX Languages)

<!-- [![Live Demo](https://img.shields.io/badge/GitHub%20Pages-Live-2ea44f?logo=github)](https://zepam.github.io/TranslationToolEvaluation/) -->

This dataset contains **parallel translations between English and XX world languages**, with approximately **XX sentence pairs per language**.  
It is designed to support low-resource MT research, evaluation, benchmarking, linguistics, and multilingual NLP education.

This dataset is designed to serve two complementary objectives.

Practically, it provides emergency management officials and message originators with a trusted repository of pre-translated alerts and message templates that can be deployed or quickly adapted during incidents. That reuse both speeds multilingual outreach and reduces the workload on already stretched staff, enabling agencies to focus their time and resources on other critical response tasks.

Scientifically, the corpus helps close a persistent gap: many low -resource languages are poorly represented in parallel data, which constrains research and system development for those communities. Consequently, building even modest, high-quality parallel collections can be impactful. By combining immediate operational utility with careful documentation and provenance, this project both supports current emergency - communication needs and creates a reusable resource for developing better multilingual tools and QA processes for future use.

## 📦 Contents

- XX languages × XX English-source sentences each
- XX different alert types (extreme heat, wind, etc.)
- Cleaned and normalized text in `data/processed`
- JSONL format and line-aligned format
- Metadata including language codes, domains, and sources. Hopefully.
- Scripts for preprocessing, combining, and generating statistics
  - the `README` file in the scripts directory will give you more information
- Notebook for data analysis

## File Name Format

### Raw Files

`SOURCE_scenario.filetype`

ex: `CITY_911_outage.csv` is a csv file containing translations about 911 outages from CITY (or county, etc.).
<!-- 
## GitHub Pages Demo

This repository includes a static demo at [demo/index.html](demo/index.html) that can be published with GitHub Pages.
For a full walkthrough of demo files and run modes, see [demo/README.md](demo/README.md). -->
