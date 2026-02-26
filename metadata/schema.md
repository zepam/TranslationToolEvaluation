# Dataset Schema

Each line in the JSONL files contains:

| Field            | Type   | Description                                        |
|------------------|--------|----------------------------------------------------|
| id               | string | Unique identifier: `{src_lang}-{tgt_lang}-{index}` |
| source_lang      | string | Source language code (ISO 639-3)\*                 |
| target_lang      | string | Target language code                               |
| source_string    | string | Source sentence in English                         |
| target_string    | string | Target translation                                 |
| situation        | string | Situation category (flood, fire, 911 outage, etc.) |
| original_source  | string | Original source of the translation strings         |
| license          | string | license information                                |


\* these are three character codes

