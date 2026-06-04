# Multi-Tagging Plan For Alerts

## Goal
Allow one alert to appear under more than one alert type in the demo, such as both `extreme_heat` and `general`.

## 1) Add Multi-Tag Support In Data
- Keep the existing `scenario` field for backward compatibility.
- Add an optional `tags` array per record.
- Example:

```json
{
  "id": "portland-extreme_heat-039",
  "scenario": "extreme_heat",
  "tags": ["extreme_heat", "general"],
  "source": {"eng": "Call 211 or visit 211info.org to get help."}
}
```

## 2) Update Demo Filtering Logic
- In `demo/index.html`, compute an alert's effective tags as:
  - all values in `tags` (if present), plus
  - `scenario` as a fallback/default tag.
- Scenario filter should match if the selected value exists in that effective tag set.
- To support cross-category discovery, filtering should scan all scenario files and match by tags, not only by file name.
- Render all tags in the alert header so users can see why the alert matched.

## 3) Bulk Tagging Workflow
- Build a generic batch process with two phases:
  - Suggestion phase (dry run): detect candidate tags and write a review report.
  - Apply phase: write approved tags back into JSONL records.
- Keep a human-review step between suggestion and apply.
- Log file-level counts (`scanned`, `changed`) for traceability.

### Pseudocode: Bulk Suggestion + Apply

```text
INPUT: list_of_jsonl_files, tagging_rules, apply_changes (true/false)
OUTPUT: updated_jsonl_files (optional), suggestions_report

initialize suggestions_report = []
initialize totals = { scanned: 0, changed: 0 }

for each file in list_of_jsonl_files:
    records = read_jsonl(file)
    file_changed = 0

    for each record in records:
        totals.scanned += 1

        effective_tags = normalize(record.tags + [record.scenario])
        proposed_tags = effective_tags

        source_text = get_english_source_text(record)

        for each rule in tagging_rules:
            if rule.matches(source_text):
                proposed_tags = union(proposed_tags, rule.tags_to_add)

        if proposed_tags != effective_tags:
            file_changed += 1
            totals.changed += 1

            append suggestions_report with {
                file, record.id, tags_before: effective_tags,
                tags_after: proposed_tags, matched_rules
            }

            if apply_changes:
                record.tags = proposed_tags

    if apply_changes and file_changed > 0:
        write_jsonl(file, records)

write_report(suggestions_report)
print totals
```

### Pseudocode: Rule Examples

```text
if source_text contains "call 211" or "211info.org":
    add tag "general"

if source_text contains generic resource-navigation language
   (for example "find help", "interactive map", "download app"):
    add tag "general"
```

## 4) Seed Example
Tag this alert with both types:
- `portland-extreme_heat-039`
- Add `"tags": ["extreme_heat", "general"]`

Apply the same change in both:
- `data/processed/portland/portland_extreme_heat.jsonl`
- `demo/data/portland_extreme_heat.jsonl`

## Notes
- This approach is backward-compatible because records without `tags` still work via `scenario`.
- Keep `tags` constrained to known taxonomy values (for example: `general`, `extreme_heat`, `flood`, etc.) to avoid drift.

### Pseudocode: Effective Tag Computation In UI

```text
function getEffectiveTags(alert):
  tags = []

  if alert.tags exists:
    tags = normalize(alert.tags)

  if alert.scenario is not empty:
    tags = union(tags, [alert.scenario])

  return tags

function matchesScenarioFilter(alert, selected_scenario):
  if selected_scenario is empty:
    return true
  return selected_scenario in getEffectiveTags(alert)
```
