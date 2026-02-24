# Dataset Codebook — Minimal Taxonomy for Emergency Alerts

This codebook defines the minimal fields used to index, summarize, and validate records in the anonymized emergency-alert dataset. All definitions, allowed values, validation rules, and examples are provided so processing and reporting are reproducible.

## Required fields (per record)

- id  
  - Type: string  
  - Description: Stable identifier for the record. Must be unique within the dataset.  
  - Example: `portland-911_outage-000`

- scenario
  - Type: controlled string  
  - Description: Primary event/hazard label for the alert. Use a controlled vocabulary.  
  - Recommended vocabulary (examples): `911_outage`, `evacuation_order`, `shelter_in_place`, `wildfire`, `flood`, `hurricane`, `tornado`, `power_outage`, `chemical_spill`, `advisory`, `test`  
  - Validation: value must be in the documented vocabulary or `unknown`.  
  - Example: `911_outage`

- source_text  
  - Type: string (Unicode)  
  - Description: The original extracted alert text. Preserve placeholders verbatim. Text should be normalized to Unicode NFC and trimmed of extraneous page headers/footers where feasible.  
  - Example: `911 is not working in {county}.`

- source_language  
  - Type: BCP‑47 language tag (string)  
  - Description: Language of `source_text`. Use canonical BCP‑47 tags (e.g., `en`, `es`, `zh-Hant`).  
  - Validation: conforms to BCP‑47 pattern and maps via `language_map` where legacy codes appear.  
  - Example: `en`

- translations
  - target_language  
    - Type: BCP‑47 language tag (string)  
    - Description: Language of the translation contained in `translation_text`. If a record contains multiple translations, either store them as a map `translations: {lang: text}` or create one record per target language.  
    - Example: `es`

  - translation_text  
    - Type: string (Unicode)  
    - Description: Translated alert text corresponding to `target_language`. Preserve placeholders. May be empty if no translation exists.  
    - Example: `El 911 no está funcionando en {county}.`

  - translation_source  
    - Type: controlled string  
    - Description: Provenance of the translation.  
    - Allowed values: `human`, `machine`, `human_post_edited_machine`, `unknown`  
    - Validation: must be one of the allowed values.  
    - Example: `human`

  - length_chars  
    - Type: integer  
    - Description: Number of Unicode characters in the translated text (call with Unicode NFC). Use for reporting and length-based grouping.  
    - Example: `27`

  - length_tokens  
    - Type: integer  
    - Description: Token count using the documented tokenizer for the language (int). Note: Tokenization is language‑dependent; record tokenizer name/version.  
    - Example: `5`

- contains_placeholders  
  - Type: boolean  
  - Description: True if the text contains variable placeholders (e.g., `{county}`, `{number}`).  
  - Detection: use regex `\{[^}]+\}` to detect placeholders.  
  - Example: `true`

- placeholders  
  - Type: list of strings (optional)  
  - Description: Exact placeholder tokens found in the text, preserved verbatim.  
  - Example: `["{county}"]`



## Validation rules and checks
- Placeholders parity: When `contains_placeholders` is true, verify that `placeholders` lists the same tokens for source and translation when the template requires exact preservation. Flag mismatches for QA.  
- Language tags: Validate `source_language` and `target_language` against BCP‑47; unmapped legacy codes should be canonicalized via `language_map` or flagged.  
- Translation presence: If `translation_source` is one of `{human, machine, human_post_edited_machine}`, then `translation_text` must be non-empty.  
- Tokenizer reporting: Record tokenizer name and version (e.g., "stanza v1.4.0, en model 1.3") in dataset metadata and methods.

## Reporting note
- When reporting aggregate metrics, explicitly state the tokenizer and version used (e.g., Stanza vX.Y models downloaded on YYYY‑MM‑DD) because length_tokens and vocab size are tokenization‑dependent.

## Example record
```json
{
  "id": "portland-911_outage-000",
  "event_type": "911_outage",
  "source_text": "911 is not working in {county}.",
  "source_language": "en",
  "target_language": "spa",
  "translation_text": "El 911 no está funcionando en {county}.",
  "translation_source": "human",
  "contains_placeholders": true,
  "placeholders": ["{county}"],
  "length_chars": 30,
  "length_tokens": 7
}