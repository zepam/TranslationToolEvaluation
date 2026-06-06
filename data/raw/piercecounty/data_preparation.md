- File Pierce County LEP - Pre-scripted Translated Messages.xlsx downloaded from URL on 04 June 2026.
- Each event (911 outage, boil water, etc.) saved as a CSV UTF-8 file.
- Twelve separate files created.

- Various length underscores were used as placeholders. All underscore placeholders were replaced with `[PLACEHOLDER]`, `[LOCATION]`, `[DATE]`, OR `[TIME]` where appropriate

## Edits made to files: ##

### piercecounty_911_outage ###

- Spanish translations were saved as incomplete sentences (fill in the blank), with the other sentence parts in a different cell. These parts were put together into one cell. The translations remained unchanged.

### piercecounty_monthly_lahar siren_test.csv ###

- Placeholders were missing for emergency number for all languages except Korean. Added `[PLACEHOLDER]` to the templates.
- `(Date)` placeholder changed to `[DATE]` to match placeholder conventions.
- `[DATE]` was missing from all translations except spanish. It was added.
- `Evacuate to: __________` changed to `Evacuate to: [LOCATION]`
- `Shelter Location: [____________]` changed to `Shelter Location: [LOCATION]`

### piercecounty_volcano_lahar.csv ###

- Spanish translations were saved as incomplete sentences, with the other sentence parts in a different cell. These parts were put together into one cell. The translations remained unchanged.

### piercecounty_weather_alert ###

- Refer to the National Weather Service for more information: ____. Replaced with `[PLACEHOLDER]`
- Added `[PLACEHOLDER]` to end of Korean translation.
- All "The National Weather Service has issued a..." alerts were done as fill-in-the-blank. The alerts were completed for all languages.
- In: `The National Weather Service has issued a ______ _______ for parts of Pierce County.` the underscores were replaced with `[PLACEHOLDER]`
- `·         ` was removed from leading event types when listed separately. "severe weather", "wind", etc.
- Vietnamese also include translations for "warning", "follow-up notification", and "disclaimer". No other languages included these words.
- Note: no Spanish translations for "The National Weather Service... alert/watch/advisory/warning" messages.