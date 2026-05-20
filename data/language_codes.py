# language_codes = {
#     "Amharic": "amh",
#     "Arabic": "ara",
#     "Burmese": "bur",
#     "Chuukese": "chk",
#     "English": "eng",
#     "Persian": "fas",  # originally persian/farsi
#     "French": "fra",
#     "Hindi": "hin",
#     "Hmong": "hmn",
#     "Japanese": "jpn",
#     "Karen": "kar",
#     "Khmer": "khm",
#     "Korean": "kor",
#     "Lao": "lao",
#     "Marshallese": "mah",
#     "Mien": "ium",        # Iu Mien
#     "Nepali": "nep",        # nepali macrolanguage
#     "Oromo": "orm",
#     "Pashto": "pus",        # pashto/pushto macrolanguage
#     "Romanian": "ron",
#     "Rohingya": "rhg",
#     "Russian": "rus",
#     "Serbian": "srp",
#     "Simplified Chinese": "zh-Hans", #check to see which is being used
#     "Somali": "som",
#     "Spanish": "spa",
#     "Swahili": "swa",
#     "Tagalog": "tgl",
#     "Telugu": "tel",
#     "Thai": "tha",
#     "Traditional Chinese": "zh-Hant", #check to see which is being used
#     "Ukrainian": "ukr",
#     "Vietnamese": "vie",
# }

language_codes = {
    "Amharic": {"iso639-2": "amh", "iso639-1": "am", "BCP-47": None},
    "Arabic": {"iso639-2": "ara", "iso639-1": "ar", "BCP-47": None},
    "Burmese": {"iso639-2": "bur", "iso639-1": "my", "BCP-47": None},
    "Chuukese": {"iso639-2": "chk", "iso639-1": None, "BCP-47": None},
    "English": {"iso639-2": "eng", "iso639-1": "en", "BCP-47": None},
    "Persian": {"iso639-2": "fas", "iso639-1": "fa", "BCP-47": None},
    "French": {"iso639-2": "fra", "iso639-1": "fr", "BCP-47": None},
    "Hindi": {"iso639-2": "hin", "iso639-1": "hi", "BCP-47": None},
    "Hmong": {"iso639-2": "hmn", "iso639-1": None, "BCP-47": None},
    "Japanese": {"iso639-2": "jpn", "iso639-1": "ja", "BCP-47": None},
    "Karen": {"iso639-2": "kar", "iso639-1": None, "BCP-47": None},
    "Khmer": {"iso639-2": "khm", "iso639-1": "km", "BCP-47": None},
    "Korean": {"iso639-2": "kor", "iso639-1": "ko", "BCP-47": None},
    "Lao": {"iso639-2": "lao", "iso639-1": "lo", "BCP-47": None},
    "Marshallese": {"iso639-2": "mah", "iso639-1": "mh", "BCP-47": None},
    "Mien": {"iso639-2": "ium", "iso639-1": None, "BCP-47": None},
    "Nepali": {"iso639-2": "nep", "iso639-1": "ne", "BCP-47": None},
    "Oromo": {"iso639-2": "orm", "iso639-1": "om", "BCP-47": None},
    "Pashto": {"iso639-2": "pus", "iso639-1": "ps", "BCP-47": None},
    "Punjabi": {"iso639-2": "pan", "iso639-1": "pa", "BCP-47": None},
    "Romanian": {"iso639-2": "ron", "iso639-1": "ro", "BCP-47": None},
    "Rohingya": {"iso639-2": "rhg", "iso639-1": None, "BCP-47": None},
    "Russian": {"iso639-2": "rus", "iso639-1": "ru", "BCP-47": None},
    "Serbian": {"iso639-2": "srp", "iso639-1": "sr", "BCP-47": None},
    "Simplified Chinese": {"iso639-2": "zh", "iso639-1": "zh", "BCP-47": "zh-Hans"},
    "Somali": {"iso639-2": "som", "iso639-1": "so", "BCP-47": None},
    "Spanish": {"iso639-2": "spa", "iso639-1": "es", "BCP-47": None},
    "Swahili": {"iso639-2": "swa", "iso639-1": "sw", "BCP-47": None},
    "Tagalog": {"iso639-2": "tgl", "iso639-1": "tl", "BCP-47": None},
    "Telugu": {"iso639-2": "tel", "iso639-1": "te", "BCP-47": None},
    "Thai": {"iso639-2": "tha", "iso639-1": "th", "BCP-47": None},
    "Traditional Chinese": {"iso639-2": "zh", "iso639-1": "zh", "BCP-47": "zh-Hant"},
    "Ukrainian": {"iso639-2": "ukr", "iso639-1": "uk", "BCP-47": None},
    "Vietnamese": {"iso639-2": "vie", "iso639-1": "vi", "BCP-47": None},
}

# language_codes_reversed = {v: k for k, v in language_codes.items()}

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