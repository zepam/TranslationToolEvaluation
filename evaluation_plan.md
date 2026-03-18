## Benchmark Now with Existing Human Translations

### 1) Prepare Splits and Gold References

- Create a held-out **test set** (e.g., hash-based split by `doc_id`) as the canonical benchmark.
- Ensure each test record includes:
    - `source_text`
    - `source_language`
    - `reference_translation` (human)
    - `translation_source` metadata

### 2) Run Reference-Based Automatic MT Metrics

- Compute:
    - **sacreBLEU** (include signature)
    - **chrF / chrF++**
    - **TER**
    - **COMET / BLEURT** (if available)
- Report results per language and aggregated.
- Document exact preprocessing/tokenizer name and version.

### 3) Run Domain-Aware Automatic Checks (Essential)

- **Placeholder fidelity:** percent preserving placeholders exactly (regex: `r'{[^}]+}'`); treat as must-pass for operations.
- **Critical-term preservation:** verify key terms (e.g., “evacuate”, “shelter”, locations, times, phone numbers) appear in outputs.
- **Numeric/NER parity:** compare numbers, dates, and named entities between reference and system outputs.
- **Slot Error Rate (SER):**  
    `SER = (#missing + #incorrect slots) / total_slots`

### 4) Produce Summary Tables and Error Examples

- Recommended table columns:
    - `#docs`, `#sentences`, `BLEU`, `chrF`, `COMET`,
    - `placeholder_fidelity(%)`, `critical_term_preserve(%)`,
    - `avg_tokens`, `vocab_size`
- Include representative failure examples per language and event type.

Also provide error category breakdowns (e.g., omitted action, mistranslated location, placeholder corruption) with examples.

---

## Practical Tooling and Code Pointers

- **sacreBLEU:** `pip install sacrebleu` (record signature)
- **COMET:** use published checkpoints
- **Placeholder parity:** regex `r'{[^}]+}'` across source/reference/system