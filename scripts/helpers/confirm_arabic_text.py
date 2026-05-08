#!/usr/bin/env python3
import unicodedata
import difflib

text_excel = """يسري التحذير من تسونامي لـ [SENDING AGENCY]: [LOCATION] حتى [TIME]. قد تؤثر سلسلة من الأمواج القوية والتيارات القوية على السواحل القريبة منك. أنت في خطر. ابتعد عن المياه الساحلية. انتقل الآن إلى أرض مرتفعة أو نحو البر. ابتعد عن الساحل حتى يصرح المسؤولون المحليون أنه من الآمن العودة."""
text_fcc = """[SENDING AGENCY]: يسري التحذير من تسونامي ل
[LOCATION] حتى [TIME]. قد تؤثر سلسلة من الأمواج
القوية والتيارات القوية على السواحل القريبة منك. أنت في خطر .
ابتعد عن المياه الساحلية. انتقل الآن إلى أرض مرتفعة أو نحو
البر. ابتعد عن الساحل حتى يصرح المسؤولون المحليون أنه من
الآمن العودة ."""


def normalize(text):
    return " ".join(text.split())

n1 = normalize(text_fcc)
n2 = normalize(text_excel)

print("=== Normalized Texts ===")
print(f"text1: {n1}\n")
print(f"text2: {n2}")

print("=== Word-level diff (normalized) ===")
words1 = n1.split()
words2 = n2.split()

matcher = difflib.SequenceMatcher(None, words1, words2)
diffs = []
for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "equal":
        continue
    w1 = " ".join(words1[i1:i2])
    w2 = " ".join(words2[j1:j2])
    diffs.append((tag, w1, w2))
    print(f"\n  [{tag.upper()}]")
    if w1:
        print(f"    text1: {w1}")
    if w2:
        print(f"    text2: {w2}")

print(f"\n=== Summary ===")
print(f"text1 word count : {len(words1)}")
print(f"text2 word count : {len(words2)}")
print(f"Total differences: {len(diffs)}")
print(f"Texts match      : {n1 == n2}")