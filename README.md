# Multilingual Emergency Translation Dataset

## Table of Contents

1. [Overview](#overview)
2. [Problem Context](#problem-context)
3. [Current Dataset Snapshot](#current-dataset-snapshot)
4. [Repository Components](#repository-components)
5. [Data Processing Workflow](#data-processing-workflow)
6. [Research and Evaluation Use Cases](#research-and-evaluation-use-cases)
7. [Design Principles](#design-principles)
8. [Intended Audience](#intended-audience)
9. [Project Status](#project-status)

## Overview

This project builds and maintains a multilingual parallel corpus focused on public safety and emergency communication. The repository contains data, metadata, scripts, and demo assets for creating structured translation resources from emergency alert content and producing analysis-ready outputs for research and evaluation.

The dataset is designed to support machine translation evaluation, low-resource language analysis, and multilingual NLP workflows where accuracy, terminology preservation, and placeholder handling are critical.

## Problem Context

Emergency alerts must be translated quickly and accurately across many languages. In practice, translation quality can vary across language pairs and event domains (for example, wildfire, flood, evacuation). This project addresses that gap by:

- consolidating multilingual alert content into consistent JSONL formats
- preserving source/translation structure and placeholder tokens
- profiling language and domain coverage
- generating reproducible summary tables for reporting and benchmarking

## Current Dataset Snapshot

Based on the current combined profile in [data/stats/combined_data_profile.json](data/stats/combined_data_profile.json):

- Total alerts: 1,793
- Languages represented: 37
- Alert/event categories represented: 34
- Primary domains include high-volume categories such as extreme heat, wildfire, evacuation, and air quality

Domain frequency outputs are available in [data/stats/domain_counts.csv](data/stats/domain_counts.csv).

## Repository Components

- Raw and processed data assets under [data](data)
- Metadata and schema documentation under [metadata](metadata), including the [processed data schema](metadata/processed_data_schema.md)
- Processing and reporting scripts under [scripts](scripts)
- A web demo interface under [demo](demo)

The scripts support end-to-end workflows from CSV ingestion to JSONL conversion, tokenization/statistics profiling, and LaTeX table generation.

## Data Processing Workflow

At a high level, the project pipeline is:

1. Ingest source translation files (CSV/Excel/API outputs)
2. Normalize and convert records to JSONL
3. Tokenize and compute per-language and per-domain statistics
4. Combine profiles across sources
5. Export publication-ready tables (CSV/LaTeX)

## Research and Evaluation Use Cases

- Benchmarking MT systems on emergency-domain text. The evaluation planning notes in [docs/evaluation_plan.md](docs/evaluation_plan.md) outline metric options such as BLEU/chrF/COMET and domain-aware checks.
- Measuring translation coverage by language and event type
- Evaluating placeholder fidelity and critical term preservation
- Building per-language token and vocabulary profiles
- Producing reproducible tables for reports and papers
- Creating thorough and useful prompts for LLMs to create correct and useful alert messaging. Or at least testing out the possibility of getting correct and useful messages as output.

## Design Principles

- Reproducibility: script-driven transformations and deterministic outputs
- Traceability: explicit source-to-processed data flow
- Practicality: outputs aligned to analysis and publication needs
- Multilingual robustness: language-aware tokenization and normalization

## Intended Audience

- Researchers in machine translation and multilingual NLP
- Public-sector and civic tech practitioners working on multilingual alerting
- Students and instructors using real-world multilingual data for coursework

## Project Status

The repository currently provides a functional data-processing toolkit and a combined multilingual profile with established reporting outputs. Ongoing work can expand language coverage, improve quality controls, and formalize benchmark splits for model comparison.

## 📦 Contents

- XX languages × XX English-source sentences each
- XX different alert types (extreme heat, wind, etc.)
- Cleaned and normalized text in `data/processed`
- JSONL format and line-aligned format
- Metadata including language codes, domains, and sources. Hopefully.
- Scripts for preprocessing, combining, and generating statistics
  - the `README` file in the scripts directory will give you more information
- Notebook for data analysis

<!-- ## File Name Format

### Raw Files

`SOURCE_scenario.filetype`

ex: `CITY_911_outage.csv` is a csv file containing translations about 911 outages from CITY (or county, etc.). -->

------------------------------------------------------

*this file was last updated on: 06 June 2026*
