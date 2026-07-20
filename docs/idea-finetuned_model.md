## Summary

Use Helsinki / OPUS‑MT (Marian) models as the easiest, transparent, local baseline. They are trained on OPUS parallel corpora and are available on Hugging Face (e.g., Helsinki-NLP/opus-mt-en-xx).

For stronger multilingual single-models trained locally from parallel corpora, use MarianNMT (the Marian framework) or Fairseq transformer training with OPUS data.

For domain adaptation, fine‑tune Marian/MarianMT or mBART on alert parallel data (augment with OPUS in-domain subsets).

Always apply entity-preserving placeholders before training and constrained postprocessing at inference.

## Why OPUS / Helsinki (Marian)?

OPUS is a curated, documented collection of parallel corpora (Europarl, Tatoeba, GNOME, JW300 etc.). Helsinki/OPUS‑MT models are trained explicitly on OPUS subsets — training data is documented and open.
Marian models are lightweight, fast for inference, and easy to run locally (no closed weights, no opaque web-crawled CC mixes).

## Quick Start
### A) Quick local inference (try existing OPUS‑MT models)
This establishes baseline translation quality for languages without training.

`pip install transformers sentencepiece sacrebleu`

Example (Python) — English → Hindi and English → Simplified Chinese:

  
```python
from transformers import MarianTokenizer, MarianMTModel

def translate(texts, model_name):
    tok = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    batch = tok(texts, return_tensors="pt", padding=True)
    translated = model.generate(**batch, max_length=256)
    return [tok.decode(t, skip_special_tokens=True) for t in translated]
```

### examples
```python
print(translate(["If you cannot reach 911, call 206-583-2111."], "Helsinki-NLP/opus-mt-en-hi"))
print(translate(["If you cannot reach 911, call 206-583-2111."], "Helsinki-NLP/opus-mt-en-zh"))
```

Models: Use the HF model naming pattern: Helsinki-NLP/opus-mt-<src>-<tgt>; they exist for many language pairs. Check Hugging Face for exact model IDs.

### B) Preprocess for high accuracy (entity placeholders)
Before training or inference, replace entities with placeholders so the model doesn’t rewrite them.

Detect entities in the source (phones, times, bracketed placeholders):


Regex for phone numbers (digits, +, parentheses).
Bracket placeholder detection: `[LOCATION]`, `[TIME]`, `[SENDING AGENCY]`.


Replace them with tokens before tokenization:


`[PHONE_1]`, `[LOCATION_1]`, etc.
After translation, reinsert the original surface forms.

### Example:
  
```python
import re
phone_re = re.compile(r'\+?\d[\d\-\s\(\)]{6,}\d')
phones = phone_re.findall(src)
src_masked = phone_re.sub(lambda m: f"[PHONE_{phones.index(m.group(0))+1}]", src)
```

translate src_masked -> tgt_masked

then replace placeholders in target with original phones

## C) Fine‑tune a Marian (Helsinki) model on alert data (domain adaptation)

Prepare parallel data files (TSV or JSONL) train.en, train.xx (one sentence per line). If [S1/S2/S3 canonical pairs](s1s2s3.md) exist, fine-tune on those.

Tokenizer: use the pretrained Marian tokenizer (or train SentencePiece jointly if scripts are available). Using the existing Marian tokenizer is easiest.

Example using Hugging Face Seq2SeqTrainer (pseudo):
  
```python
from transformers import MarianTokenizer, MarianMTModel, Seq2SeqTrainer, Seq2SeqTrainingArguments
from datasets import load_dataset

model_name = "Helsinki-NLP/opus-mt-en-zh"  # choose base
tok = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

ds = load_dataset('csv', data_files={'train':'train.csv','validation':'dev.csv'})
```

### tokenization map, map to model inputs outputs

```python
def preprocess(examples):
    inputs = examples['en']
    targets = examples['zh']
    model_inputs = tok(inputs, max_length=256, truncation=True, padding='max_length')
    labels = tok(targets, max_length=256, truncation=True, padding='max_length').input_ids
    model_inputs['labels'] = labels
    return model_inputs

tokenized = ds.map(preprocess, batched=True)
training_args = Seq2SeqTrainingArguments(output_dir="out", per_device_train_batch_size=8, num_train_epochs=3, predict_with_generate=True)
trainer = Seq2SeqTrainer(model=model, args=training_args, train_dataset=tokenized['train'], eval_dataset=tokenized['validation'])
trainer.train()
trainer.save_model("outputs/domain-marian")
```


Use smaller batch size and mixed precision if limited GPU.

## D) Evaluate (automatic and human)

Use chrF++, BLEU, embedding cosine (LaBSE) for semantic check.

Critically evaluate entity preservation — compute exact match rate for placeholders in target.

Human spot-check (5–10 bilingual reviewers) for action fidelity and harmful omissions.

## E) Constrained decoding / copy mechanism

Ensure placeholders are preserved:

Use forced copy for tokens like [PHONE_1] by adding them to bad_words_ids? or better: keep placeholders in source and they are likely copied if they are single tokens.

For more control: use constrained decoding libraries or mask tokens as required.

## F) Multi‑language single-model (optional)

For one model to handle many target languages, pre-finetune different Helsinki models per pair or train a multilingual model (e.g., mBART or mT5). But training a big multilingual model requires more compute.
A practical route: fine-tune one base Marian per language pair, or create small per-language adapters (AdapterHub) for a single runtime.

## G) Dataset & training-data provenance (important)

OPUS-based Helsinki models are explicit about the corpora used; if building a model from scratch, keep a manifest of training sources (OPUS subsets, alert corpus) so provenance is known.
For transparency, keep a training_manifest.json describing data sources & license.

## H) Deployment & integration

- Wrap translator in a small local service (FastAPI).
- Pre- and post-process (entities, placeholders, QA checks).
- Provide confidence metrics: chrF to canonical English, or token‑level log‑probabilities.
- For production: require manual review for critical languages; have an immediate fallback to human translation or template in case of low confidence.

## I) Safety: guardrails

- Block any output that changes a placeholder or inserts a new phone or URL not in the source, unless confirmed by human.

- Add an “entity diff” stage: if entities differ, mark as critical and require human review.

- Log every automatic output; require traceability.

- Keep an opt‑out: automatic translations feed to a queue for translators; only publish once human approves.

## J) Compute & tooling

- For fine‑tuning Marian / mT5-small:

    - Single GPU (16–24GB) is OK for small experiments.
    - Use mixed precision (fp16) via accelerate or trainer.

For inference on many languages: consider CPU inference with Marian (fast) or deploy on an inference GPU.

## K) Concrete next steps & checklist (first 2 weeks)

### Quick baseline (1–2 days):

Run OPUS-MT Helsinki model inference on representative alerts (English→target languages) to see baseline quality.


### Prepare training corpus (2–5 days):

Extract aligned S1/S2/S3 pairs; create train/dev/test (2k–10k pairs if possible).
Replace entities with placeholders.


### Prototype fine‑tune (3–7 days):

Fine-tune Marian/mT5-small on one language pair (e.g., en→hi or en→zh).


### Evaluate and add entity checks (2–3 days).
Build a small FastAPI wrapper that exposes translate + entity diff (2–4 days).
### Pilot human review flow and iterate.

## L) Example: English → Simplified Chinese local prototype (commands)

Try Helsinki inference first (as shown earlier).
To fine-tune, use the Seq2SeqTrainer snippet above. Monitor entity preservation.

## M) Which languages to prioritize?

Pick languages with:

- High local population or operational need
- Low baseline MT quality in tests
- Good amount of parallel data for fine‑tuning

Try 2–4 target languages to prototype first (e.g., Hindi, Simplified Chinese, Amharic, Tagalog) 
