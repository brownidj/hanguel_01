from __future__ import annotations

from pathlib import Path

import yaml

from app.domain.romanization_rr import romanize_cv, romanize_text


def test_rr_romanize_cv_basic() -> None:
    assert romanize_cv("ㄱ", "ㅏ").rr == "ga"
    assert romanize_cv("ㄷ", "ㅓ").rr == "deo"
    hint = romanize_cv("ㅅ", "ㅣ").hint.lower()
    assert "sh" in hint or "shi" in hint


def test_rr_vowel_table_complete() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "vowels.yaml"
    raw = data_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    items = data.get("vowels", [])
    glyphs = []
    for item in items:
        if isinstance(item, dict):
            glyph = item.get("glyph")
            if isinstance(glyph, str):
                glyphs.append(glyph)
    assert glyphs
    for vowel in glyphs:
        result = romanize_cv("∅", vowel)
        assert result.rr, "Missing RR mapping for vowel {}".format(vowel)


def test_rr_consonant_table_complete() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "consonants.yaml"
    raw = data_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    items = data.get("consonants", [])
    glyphs = []
    for item in items:
        if isinstance(item, dict):
            glyph = item.get("glyph")
            if isinstance(glyph, str):
                glyphs.append(glyph)
    assert glyphs
    for consonant in glyphs:
        result = romanize_cv(consonant, "∅")
        if consonant == "ㅇ":
            assert result.rr == ""
        else:
            assert result.rr, "Missing RR mapping for consonant {}".format(consonant)


def test_rr_syllable_pairs_have_rr() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "syllables.yaml"
    raw = data_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    items = data.get("syllables", [])
    assert items
    for item in items:
        if not isinstance(item, dict):
            continue
        consonant = item.get("consonant")
        vowel = item.get("vowel")
        if not isinstance(consonant, str) or not isinstance(vowel, str):
            continue
        result = romanize_cv(consonant, vowel)
        assert result.rr, "Missing RR mapping for {}{}".format(consonant, vowel)


def test_rr_romanize_text_words() -> None:
    data_path = Path(__file__).resolve().parents[1] / "data" / "examples.yaml"
    raw = data_path.read_text(encoding="utf-8")
    data = yaml.safe_load(raw) or {}
    items = data.get("examples", [])
    assert items
    for item in items:
        if not isinstance(item, dict):
            continue
        glyph = item.get("hangul")
        if not isinstance(glyph, str):
            continue
        result = romanize_text(glyph)
        assert result.rr
        assert "RR spelling" in result.hint
