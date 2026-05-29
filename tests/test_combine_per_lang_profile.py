import importlib.util
from pathlib import Path
import tempfile
import textwrap


def _load_module():
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "scripts" / "combine_per_lang_profile.py"
    spec = importlib.util.spec_from_file_location("combine_per_lang_profile", mod_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


MODULE = _load_module()


def test_normalize_placeholders_basic():
    s = "Hello { name } world { }"
    assert MODULE.normalize_placeholders(s) == "Hello {NAME} world {}"


def test_normalize_placeholders_examples():
    normalize = MODULE.normalize_placeholders
    assert normalize(None) is None
    assert normalize("Hello { name }!") == "Hello {NAME}!"
    assert normalize("Empty {} test") == "Empty {} test"
    assert normalize("{ abc123 }") == "{ABC123}"


def test_split_sentences_simple():
    s = "One. Two? Three!"
    parts = MODULE.split_sentences(s)
    assert parts == ["One.", "Two?", "Three!"]


def test_char_tokens_keep_placeholders():
    toks = MODULE._char_tokens_keep_placeholders("你{X}好")
    assert toks == ["你", "{X}", "好"]


def test_tokenize_translation_latin_with_placeholder():
    toks = MODULE.tokenize_translation("Hello { name } world", "en")
    assert toks == ["Hello", "{NAME}", "world"]


def test_tokenize_translation_cjk_and_placeholder():
    toks = MODULE.tokenize_translation("{name}你好", lang_code="zh")
    # placeholders are normalized to upper-case by normalize_placeholders
    assert toks == ["{NAME}", "你", "好"]


def test_tokenize_translation_cjk_preserves_placeholders():
    toks = MODULE.tokenize_translation("你好吗{ user }", "zh")
    assert toks == ["你", "好", "吗", "{USER}"]


def test_build_doc_texts_prefers_translations_over_source():
    obj = {
        "translations": {"en": "Translated"},
        "source": {"eng": "SourceEnglish", "fr": "SourceFrench"},
    }
    texts = MODULE.build_doc_texts(obj)
    assert texts["en"] == "Translated"
    assert texts["fr"] == "SourceFrench"
    # original 'eng' key should be normalized to 'en' and not present separately
    assert "eng" not in texts


def test_build_doc_texts_prioritizes_translations_and_normalizes_eng():
    obj = {
        "translations": {"en": "translated", "fr": "traduit", "xx": "   "},
        "source": {"eng": "source eng", "es": "fuente", "xx": "origen"},
    }

    texts = MODULE.build_doc_texts(obj)

    # translations take priority
    assert texts.get("en") == "translated"
    assert texts.get("fr") == "traduit"

    # source value used when translation is empty/whitespace
    assert texts.get("es") == "fuente"
    assert texts.get("xx") == "origen"


def test_load_language_codes():
    # Use a temporary file instead of pytest tmp_path fixture so these tests
    # can be run without pytest test harness.
    py_content = textwrap.dedent(
        """
        language_codes = {
            "English": {"iso639-1": "en"},
            "Amharic": {"iso639-1": "am"},
            "Old": {"iso639-2": "abc"},
        }
        """
    )
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "langcodes.py"
        p.write_text(py_content, encoding="utf-8")
        mapping = MODULE.load_language_codes(p, var_name="language_codes")
        assert mapping.get("en") == "English"
        assert mapping.get("am") == "Amharic"
        assert mapping.get("abc") == "Old"
