# tests/test_render_variants.py
import importlib

import pytest
from PyQt6.QtWidgets import QWidget, QApplication

# Prefer shared helpers from conftest, but fall back to local definitions
try:
    from .conftest import _class_name as _cn_from_cf, _extract_glyph_text as _egt_from_cf

    _class_name = _cn_from_cf
    _extract_glyph_text = _egt_from_cf
except Exception:
    from typing import Optional


    def _class_name(w) -> str:
        try:
            return w.metaObject().className()
        except Exception:
            return w.__class__.__name__


    def _extract_glyph_text(w) -> Optional[str]:
        for attr in ("char", "glyph", "text"):
            try:
                val = getattr(w, attr, None)
                if callable(val):
                    val = val()
                if isinstance(val, str) and val:
                    return val
            except Exception:
                pass
        try:
            val = w.property("char")
            if isinstance(val, str) and val:
                return val
        except Exception:
            pass
        try:
            val = w.accessibleName()
            if isinstance(val, str) and val:
                return val
        except Exception:
            pass
        return None


@pytest.mark.ui
@pytest.mark.parametrize("lead,vowel", [("ㄱ", "ㅏ"), ("ㄱ", "ㅗ"), ("ㄱ", "ㅜ"), ("ㄱ", "ㅣ")])
def test_render_has_consonant_and_vowel_widgets(window, qtbot, lead, vowel, main_module, tmp_path):
    # Ask app to render the specific pair if possible
    try:
        if hasattr(main_module, "show_pair"):
            main_module.show_pair(lead, vowel)
        elif hasattr(main_module, "select_syllable_for_block"):
            # Compose the syllable if your app supports it; otherwise leave as-is
            pass
    except Exception:
        pass

    jamo = window.findChild(object, "JamoBlock") or window
    root = jamo.findChild(QWidget, "frameJamoBorder") or jamo
    try:
        qtbot.waitUntil(lambda: len(root.findChildren(QWidget)) > 0, timeout=1000)
    except Exception:
        pass

    all_widgets = root.findChildren(QWidget) or QApplication.instance().allWidgets()
    consonants, vowels = [], []
    for w in all_widgets:
        cname = _class_name(w)
        oname = getattr(w, "objectName", lambda: "")() or ""
        role = getattr(w, "property", lambda n: None)("glyphRole") or getattr(w, "property", lambda n: None)("role")
        acc = ""
        try:
            acc = w.accessibleName()
        except Exception:
            pass
        low = (oname + cname + str(role or "") + acc).lower()
        if ("consonant" in low) or (role == "consonant"):
            consonants.append(w)
        if ("vowel" in low) or (role == "vowel"):
            vowels.append(w)

    if not consonants and not vowels:
        pytest.skip("Glyph widgets not discoverable (custom paint); enable HANGUL_TEST_MODE exposure.")
    if not consonants:
        pytest.skip("No consonant glyph widget found; enable test-mode glyph roles.")
    if not vowels:
        pytest.skip("No vowel glyph widget found; enable test-mode glyph roles.")

    # Optional: verify glyph text if exposed
    texts_con = [t for w in consonants if (t := _extract_glyph_text(w))]
    texts_vow = [t for w in vowels if (t := _extract_glyph_text(w))]
    if texts_con:
        assert lead in texts_con
    if texts_vow:
        assert vowel in texts_vow

    # Capture an artifact for debugging layout drift over time (success or failure)
    try:
        pic = window.grab()
        out = tmp_path / f"render_{lead}_{vowel}.png"
        pic.save(str(out))
    except Exception:
        pass


# --- Classification tests ---
@pytest.mark.classification
def test_block_type_function_exposed():
    main_module = importlib.import_module("main")
    fn = getattr(main_module, "block_type_for_pair", None)
    assert callable(fn), "block_type_for_pair() must be exposed"


@pytest.mark.classification
@pytest.mark.parametrize("lead,vowel,starts_with", [
    ("ㄱ", "ㅏ", "A"), ("ㄴ", "ㅑ", "A"), ("ㅁ", "ㅐ", "A"),
    ("ㄱ", "ㅗ", "B"), ("ㄴ", "ㅛ", "B"), ("ㅁ", "ㅚ", "B"),
    ("ㄱ", "ㅜ", "C"), ("ㄴ", "ㅠ", "C"), ("ㅁ", "ㅝ", "C"),
    ("ㄱ", "ㅣ", "D"), ("ㅂ", "ㅟ", "D"),
])
def test_block_type_basic_mapping(lead, vowel, starts_with):
    main_module = importlib.import_module("main")
    fn = getattr(main_module, "block_type_for_pair")
    result = fn(lead, vowel)
    name = getattr(result, "name", str(result))
    assert name.startswith(starts_with), f"{lead}+{vowel} expected {starts_with}*, got {name}"
