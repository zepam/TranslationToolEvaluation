language_codes = {
    "Amharic": "amh",
    "Arabic": "ara",
    "Burmese": "bur",
    "Chuukese": "chk",
    "English": "eng",
    "Persian": "fas",  # originally persian/farsi
    "French": "fra",
    "Hindi": "hin",
    "Hmong": "hmn",
    "Japanese": "jpn",
    "Karen": "kar",
    "Khmer": "khm",
    "Korean": "kor",
    "Lao": "lao",
    "Marshallese": "mah",
    "Mien": "ium",        # Iu Mien
    "Nepali": "nep",        # nepali macrolanguage
    "Oromo": "orm",
    "Pashto": "pus",        # pashto/pushto macrolanguage
    "Romanian": "ron",
    "Rohingya": "rhg",
    "Russian": "rus",
    "Serbian": "srp",
    "Simplified Chinese": "zh-Hans", #check to see which is being used
    "Somali": "som",
    "Spanish": "spa",
    "Swahili": "swa",
    "Tagalog": "tgl",
    "Telugu": "tel",
    "Thai": "tha",
    "Traditional Chinese": "zh-Hant", #check to see which is being used
    "Ukrainian": "ukr",
    "Vietnamese": "vie",
}

language_codes_reversed = {v: k for k, v in language_codes.items()}

language_codes_to_iso = {
    "amh": "am",
    "ara": "ar",
    "bur": "my",
    "chk": "chk",  # no ISO 639-1 code for Chuukese
    "eng": "en",
    "fas": "fa",
    "fra": "fr",
    "hin": "hi",
    "hmn": "hmn",  # no ISO 639-1 code for Hmong
    "jpn": "ja",
    "kar": "kar",  # no ISO 639-1 code for Karen
    "khm": "km",
    "kor": "ko",
    "lao": "lo",
    "mah": "mah",  # no ISO 639-1 code for Marshallese
    "nep": "ne",
    "orm": "om",
    "pus": "ps",
    "ron": "ro",
    "rhg": "rhg",  # no ISO 639-1 code for Rohingya
    "rus": "ru",
    "srp": "sr",
    "som": "so",
    "spa": "es",
    "swa": "sw",
    "tel": "te",
    "tgl": "tl",
    "tha": "th",
    "ukr": "uk",
    "vie": "vi",
}