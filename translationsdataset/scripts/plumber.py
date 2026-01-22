# requires: pip install pdfplumber pandas ftfy langdetect
import pdfplumber, re, pandas as pd
from ftfy import fix_text
from langdetect import detect

pdf_path = "/home/jen/TranslationsDataset/translationsdataset/data/raw/fcc/WEA-Multilingual-Fillable-Alert-Templates-Guidance-2025.pdf"
# Example separator regex - adjust to your PDF structure
# e.g., alerts start with "Alert" followed by number or a line of dashes
alert_split_pattern = re.compile(r"\bAlert\s*\d+\b", re.IGNORECASE)

records = []
with pdfplumber.open(pdf_path) as pdf:
    full_text = []
    for pagenum, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        # optionally remove headers/footers heuristically, e.g., by page numbers
        full_text.append(f"\n\n---PAGE:{pagenum}---\n" + text)
    doc_text = "\n".join(full_text)

# Split into blocks. If the first block is preface, filter it out.
parts = alert_split_pattern.split(doc_text)
# If split returns leading empty, or split removed the delimiter, rebuild with finditer if needed.
# Alternate: use finditer to capture delimiters and text.

# Example simple parse: suppose each alert contains lines like:
# Original: <text>
# Translation: <text>
orig_re = re.compile(r"Original[:\s]+(.+?)(?=Translation:|$)", re.S|re.I)
trans_re = re.compile(r"Translation[:\s]+(.+?)(?=Original:|$)", re.S|re.I)

for part in parts:
    part = part.strip()
    if not part:
        continue
    # clean artifacts
    part = fix_text(part)
    m_orig = orig_re.search(part)
    m_trans = trans_re.search(part)
    original = m_orig.group(1).strip() if m_orig else ""
    translation = m_trans.group(1).strip() if m_trans else ""
    # language detection (best-effort)
    try:
        lang_orig = detect(original) if original else ""
    except Exception:
        lang_orig = ""
    try:
        lang_trans = detect(translation) if translation else ""
    except Exception:
        lang_trans = ""
    records.append({
        "original_text": original,
        "translated_text": translation,
        "original_lang": lang_orig,
        "translated_lang": lang_trans,
        "raw_block": part[:500]  # store snippet for traceability
    })

df = pd.DataFrame.from_records(records)
df.to_csv("alerts_extracted.csv", index=False, encoding="utf-8")
print("Wrote", len(df), "records to alerts_extracted.csv")