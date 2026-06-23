# Processed Data Schema

The processed dataset is stored as JSON Lines (`.jsonl`) files. Each line is one record.

## Record Structure

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Unique record identifier in the form `{origin}-{scenario}-{index:03d}` |
| `scenario` | string | Scenario or event category, usually derived from the file name |
| `source` | object | Source text container |
| `translations` | object | Language-to-translation map |

## Nested Objects

### `source`

| Field | Type | Description |
| --- | --- | --- |
| `eng` | string | English source text |

### `translations`

`translations` is a map whose keys are language codes and whose values are translated strings.

Example keys include `en`, `es`, `am`, `ar`, `zh-Hans`, and `zh-Hant`.

## Example Record

```json
{
  "id": "portland-general-001",
  "scenario": "general",
  "source": {
    "eng": "Safety Message from {County Name}"
  },
  "translations": {
    "en": "Safety Message from {County Name}",
    "es": "Mensaje de seguridad de {County Name}"
  }
}
```

## Notes

- Records are written one per line, so files can be streamed efficiently.
- Language codes follow the repository language mapping in `data/language_codes.py`.
- Placeholder text is preserved inside `{ }` in both source and translated strings.