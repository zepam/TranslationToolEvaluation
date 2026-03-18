## Benchmark Now with Existing Human Translations

### 1) Prepare Splits and Gold References

- Create a held-out **test set** (e.g., hash-based split by `doc_id`) as the canonical benchmark.
- Ensure each test record includes:
    - `source_text`
    - `source_language`
    - `reference_translation` (human)
    - `translation_source` metadata

### 2) Baseline systems
    - Commercial APIs: Google Translate, DeepL, Azure Translator
    - Open-source models: NLLB, M2M-100, or mBART

    Note the version, parameters, preprocessing steps

### 3) Run Reference-Based Automatic MT Metrics

- **Options**:
    - sacreBLEU
    - chrF / chrF++
    - METEOR
    - COMET
    - BLEURT
    - BERTScore
  
- Report results per language and aggregated.
- Document exact preprocessing/tokenizer name and version.

- **Also?**
  - Readability?
  - evaluate small sample. track errors by type and severity?
  - Translation error rate

### 4) Run Domain-Aware Automatic Checks

- **Placeholder fidelity:** percent preserving placeholders exactly (regex: `r'{[^}]+}'`); treat as must-pass for operations.
- **Critical-term preservation:** verify key terms (e.g., “evacuate”, “shelter”, locations, times, phone numbers) appear in outputs.
- **Numeric/NER parity:** compare numbers, dates, and named entities between reference and system outputs.
- **Slot Error Rate (SER):**  
    `SER = (#missing + #incorrect slots) / total_slots`

### 5) Produce Summary Tables and Error Examples

- Probable table columns:
    - `#docs`, `#sentences`, `BLEU`, `chrF`, `COMET`, `Other Metrics`
    - `placeholder_fidelity(%)`, `critical_term_preserve(%)`,
    - `avg_tokens`, `vocab_size`
- Include representative failure examples per language and event type.

If done in Step 3, provide error category breakdowns (e.g., omitted action, mistranslated location, placeholder corruption) with examples.

---

## Practical Tooling and Code Pointers

- **sacreBLEU:** `pip install sacrebleu` (record signature)
- **COMET:** use published checkpoints
- **Placeholder parity:** regex `r'{[^}]+}'` across source/reference/system