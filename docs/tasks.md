# 📝 TranslationToolEvaluation Task List

[ ] Not started, ⏳ In progress, ✅ Done, 🛑 Blocked

### 🔴 High Priority

- [ ] Fix language code table and verify missing languages are included
  - ✅ Chinese Traditional AND Chinese Simplified
  - [ ] Marshallese isn't mapping correctly
- ⏳ Develop licensing agreement to share with agencies
- [ ] FCC - fix the sentence parsing as detailed in `analysis_out/missing_extra_report.csv`
- ⏳ Clarify which sentences are similiar and which are essentially templates. `Flood watch` is similar to `flood warning`, but `the temp will be XX today` is a template. Many sentences are similiar, but carry an important distinction. 
- Examine placeholder names that will minimize the chances of translation. Using symbols? Strange characters? Emoji?
- [ ] Clean up placeholders to [PLACEHOLDER] [OR WHATEVER WORD WORKS BEST]
  - [ ] kc
  - [ ] pierce county
- [ ] Include *.md to indicate the file cleanup that was done
  - ✅ pierce county
  - [ ] portland
  - [ ] king county
- confirm that chinese is supported by Simplified, Traditional, and Generic (use when not specified)

### 🟠 Medium Priority

- ⏳ evaluate similarities betwen translations that are in the same language/event pair
- [ ] extract similiar functions, like tokenization, RE definitions, normalization into one helper file
- [ ] extract similiar latex table code into a single helper file to centralize formatting
- [ ] find some way to tag alerts so they can appear under different categories when appropriate

### 🟢 Low Priority

- [ ] Draft citation guidance section for organizations and data use
- [ ] Update demo with new events and languages
- [ ] Add placeholder fidelity and critical-term checks to evaluation outputs

## 🤔 Maybe?

- [ ] Add provenance notes (metadata) strategy for translation sources. Or talk about how we don't have it.
- [ ] Add timestamps/recency field for translations
- [ ] Define train/dev/test split policy and document in metadata
- [ ] Evaluate benchmark metrics on held-out set (BLEU, chrF, COMET)

