B. Multilingual QA tool for translators
Goal

Provide a practical UI & automated checks that highlight missing/extra sentences, altered entities, length/character limits, tone/register mismatches, and provide recommendations to translators and reviewers.

Key features

File ingestion and sentence alignment visualization.
Automatic checks:

Missing/extra sentence detection (per-english-sentence).
Entity preservation (phone numbers, placeholders, URLs).
Lexical divergence warning: low chrF but high semantic similarity (paraphrase OK) vs low sem & low chrF (possible mistranslation).
Tokenization sanity: suspect languages where tokens look like characters (flag).
Style/locale warnings (units, currency, scripts).


Triage dashboard: priority buckets (critical = entity mismatch, high = missing sentences, medium = long translations).
Translator workspace: side-by-side editor with suggestions, machine-suggested fixes (LLM suggestions), and one-click acceptance.
Audit trail & export: store original + corrected + reviewer notes.

Architecture & stack

Backend: FastAPI (Python) or Flask

Tasks: run splitters (stanza), compute metrics (chrF, embeddings), entity regex, language detection.
Queue: Celery or RQ for heavier tasks (embeddings, LLM calls).


ML components:

Sentence embedding service: multilingual SBERT/LaBSE model deployed locally or via HF Inference.
Tokenizer: SentencePiece joint model (from earlier).
Optional LLM API for suggestions (OpenAI, Anthropic, Gemini etc; keep human-in-loop).


Frontend: React or simple Flask server‑rendered pages

Components: file upload, per-file summary, per-row detail, inline editor, accept/reject.


Storage: SQLite/Postgres for metadata; store files in S3 or local storage.

QA checks (algorithms)

Missing/Extra:

If English cell non-empty & translation empty → missing.
If translation non-empty & English empty → extra.


Entity checks:

regex for phone numbers, digits, bracket placeholders.
compare sets; if mismatch → critical flag.


Paraphrase detection:

use SBERT embeddings; compute cosine(eng, trans) and chrF; if cosine>0.80 & chrF<30 → paraphrase (OK). If cosine<0.6 & chrF<30 → possible mismatch.


Tokenization checks:

tokens_per_char ratio; if approx 1 → likely char-level tokenization; flag for review.



Human workflow

Translators fix high/critical flags first (entities, missing sentences).
Reviewers check medium/low flags and accept.
For each file record accept/reject, reviewer note, time stamp.

Evaluation

Measure time per file for translators with vs without tool, error reduction rate on a held-out set, and rater satisfaction.

Implementation steps & deliverables

Prototype backend + simple UI to upload one CSV and run checks (3–5 days).
Add interactive editor and accept/reject flows (5–10 days).
Integrate embedding-based paraphrase detection and choose thresholds (3–5 days).
Human pilot with translators for feedback & iterate (7–14 days).
Deliverables: working web app (dockerized), docs, test suite, sample outputs.

Ethics & operational considerations

Never auto-publish translated alerts without final human signoff.
Log all edits and who approved them.
Ensure translators see original placeholders and entity warnings prominently.
Include fallback instructions for ambiguous cases.
