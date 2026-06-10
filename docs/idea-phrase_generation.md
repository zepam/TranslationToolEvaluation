A. Paraphrase generation and canonicalization for alerts
Goal

Produce canonical, template-aligned versions of emergency alerts across languages (e.g., canonical S1/S2/S3) and generate paraphrases that preserve required actions/critical entities. This enables consistent display, easier QA, and cross-language comparisons.

Why it’s useful

Normalizes heterogeneous translations so downstream checks, comparisons, and modeling operate on consistent units; reduces human effort during triage.

Data & preprocessing

Inputs: sentence-delimited dataset (aligned English + translations). Prefer rows where English S1/S2/S3 are clear.
Create a canonical target triple for each alert: S1 (header/what & where), S2 (actions to take), S3 (warning about dialing 9-1-1 etc).
Use a held-out development set (200–500 alerts) annotated with canonical text per language for evaluation and fine-tuning.
Preprocess:

Normalize placeholders: [SENDING AGENCY], [LOCATION], [TIME].
Normalize punctuation and whitespace.
Detect and preserve critical entities (phones, URLs, lat/lon) as placeholders.
Train a joint SentencePiece model (8k–32k vocab) over all languages to standardize tokenization.



Methods / Architectures (practical)

Baselines:

Prompted LLM (few-shot): Use an instruction + 3–5 examples (English→canonical English; same in language L if available). Good quick baseline.
Rule-based mapping: For templated alerts produce S1/S2/S3 using regex + keywords (cheap, high-precision for common templates).


Production approach:

Fine-tune a multilingual seq2seq model to map input sentence(s) → canonical sentence(s).
Model candidates:

mT5-small / mT5-base (good multilingual seq2seq)
mBART or T5-multilingual variants
If using hosted LLMs, instruction-tune a small adapter or use few-shot prompts for languages lacking data.


Training setup:

Input: original sentence(s) in language L (or English+L)
Target: canonical sentence(s) in language L
Loss: cross‑entropy; early stopping on dev set.
Data augmentation: round-trip translation, backtranslation, synthetic paraphrases, entity masking.




Hybrid option: pipeline using LLM prompts to produce canonical English, then translate canonical English into target languages via MT or LLM, then post-check.

Example few-shot prompt (English → canonical English)

System: “You are an alert canonicalizer. For each alert, produce three short sentences: 1) header (who/what/where), 2) actions, 3) warning (if any). Keep placeholders unchanged.”
Example: show 3 pairs (input alert → canonical S1/S2/S3).
Query: input alert text
Output format: newline-separated S1 || S2 || S3 (or JSON)

Evaluation

Automatic:

chrF++ / BLEU vs canonical target (per-language).
Entity preservation: exact match recall for phone numbers, URLs, location placeholders.
Semantic similarity: sentence-embedding cosine (LaBSE / multilingual SBERT).


Human:

Binary action-preservation (does output mention the required action(s)?)
Fluency & naturalness (Likert 1–5)
Safety check: does the canonicalized message omit or change critical info?


Success criteria:

≥95% entity recall, average human action-preservation > 0.95, average fluency ≥4.0 (Likert).



Implementation steps & deliverables

Data preparation (1–2 days): extract aligned sentences, mark canonical targets for a seed set (200–500).
Baseline: few-shot prompt evaluation across 10 languages (1–2 days).
Train seq2seq model (mT5-small) on full train set (3–7 days, iterate).
Evaluate automatic metrics and run human audit (2–5 days).
Deliverables: training notebook, trained model, evaluation report, sample canonicalized outputs.

Risks & mitigations

Risk: model hallucination changing entities — mitigate with entity placeholders, automated checks that block any output where placeholders changed.
Risk: inadequate data for low-resource languages — use transfer learning, joint tokenization, and English→target backtranslation.
