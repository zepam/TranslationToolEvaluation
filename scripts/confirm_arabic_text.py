#!/usr/bin/env python3
import unicodedata
import difflib

text1 = """[SENDING AGENCY]:  يسري التحذير من  عاصفة ترابية لـ  [LOCATION] حتى [TIME].  كن مستعدًا للانخفاض المفاجئ في مستوى الرؤية الذي قد يصل  إلى الصفر. توقف على جانب الطريق، وابق  على قيد الحياة !عندما تنخفض الرؤية، اركن سيارتك بعيدًا عن مسار الطريق، ثم ضعها في وضع الانتظار.أطفئ الأنوار وأبعد قدمك عن المكابح.حث الرضع وكبار السن وأولئك الذين يعانون من مشاكل في التنفس على اتخاذ الاحتياطات اللازمة"""

text2 = """[SENDING AGENCY]:  يسري التحذير من  عاصفة ترابية ل [LOCATION] حتى [TIME].  كن مستعدًا للانخفاض المفاجئ في مستوى الرؤية الذي قد يصل  إلى الصفر.  توقف على جانب الطريق، وابق  على قيد الحياة !عندما تنخفض  رؤية، اركن سيارتك بعيدًا عن مسار الطريق، ثم ضعها في   وضع الانتظار.أطفئ الأنوار وأبعد قدمك عن المكابح.حث الرضع وكبار السن وأولئك الذين يعانون من مشاكل في التنفس على اتخاذ الاحتياطات اللازمة"""

def normalize(text):
    return " ".join(text.split())

n1 = normalize(text1)
n2 = normalize(text2)

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