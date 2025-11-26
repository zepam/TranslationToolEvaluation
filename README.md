# Multilingual Translation Dataset (English ↔ 30+ Languages)

This dataset contains **parallel translations between English and 30+ world languages**, with approximately **50 sentence pairs per language**.  
It is designed to support low-resource MT research, evaluation, benchmarking, linguistics, and multilingual NLP education.

## 📦 Contents

- ~30 languages × 50 English-source sentences each
- Cleaned and normalized text
- JSONL format and line-aligned format
- Metadata including language codes, domains, and sources
- Train/dev/test splits
- Scripts for preprocessing, combining, and generating statistics

## 🏗️ Directory Structure

See the full directory tree in the repository root.

<!-- ## 🔥 How to Use -->

<!-- ### Load with Python
```python
import json

with open("data/splits/train.jsonl") as f:
    for line in f:
        ex = json.loads(line)
        print(ex["src"], "→", ex["tgt"]) -->
