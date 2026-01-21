from __future__ import annotations

"""Hangul composition helpers (domain layer).

This module contains *no* Qt/UI dependencies.

It centralises:
- Hangul Jamo ordering constants (compatibility jamo)
- Pure functions for composing CV / LVT syllables

Primary API:
- compose_cv(lead, vowel)
"""

from typing import Final


# -----------------------------------------------------------------------------
# Domain data: compatibility jamo ordering
# -----------------------------------------------------------------------------

# Leading consonants (Choseong) in standard Unicode Hangul order
CHOSEONG: Final[tuple[str, ...]] = (
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)

# Vowels (Jungseong) in standard Unicode Hangul order
JUNGSEONG: Final[tuple[str, ...]] = (
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ",
    "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ",
    "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ",
    "ㅡ", "ㅢ", "ㅣ",
)

# Trailing consonants (Jongseong) in standard Unicode Hangul order
# Index 0 is "no final"
JONGSEONG: Final[tuple[str, ...]] = (
    "",
    "ㄱ", "ㄲ", "ㄳ",
    "ㄴ", "ㄵ", "ㄶ",
    "ㄷ",
    "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ",
    "ㅁ",
    "ㅂ", "ㅄ",
    "ㅅ", "ㅆ",
    "ㅇ",
    "ㅈ", "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
)

# Conservative defaults used by parts of the app/tests
DEF_L: Final[str] = "ㄱ"
DEF_V: Final[str] = "ㅏ"


# -----------------------------------------------------------------------------
# Internal lookup maps
# -----------------------------------------------------------------------------

_CHO_MAP: Final[dict[str, int]] = {j: i for i, j in enumerate(CHOSEONG)}
_JUNG_MAP: Final[dict[str, int]] = {j: i for i, j in enumerate(JUNGSEONG)}
_JONG_MAP: Final[dict[str, int]] = {j: i for i, j in enumerate(JONGSEONG)}


# -----------------------------------------------------------------------------
# Domain logic
# -----------------------------------------------------------------------------

def compose_lvt(lead: str, vowel: str, tail: str = "") -> str:
    """Compose a Hangul syllable from compatibility jamo.

    Args:
        lead: choseong (e.g., "ㄱ")
        vowel: jungseong (e.g., "ㅏ")
        tail: jongseong (e.g., "ㄴ") or "" for no final

    Returns:
        A composed Hangul syllable (e.g., "간") or "" if inputs are invalid.

    Notes:
        This uses the Unicode Hangul Syllables algorithm:
        SBase + (LIndex * VCount + VIndex) * TCount + TIndex
    """
    l = (lead or "").strip()
    v = (vowel or "").strip()
    t = (tail or "").strip()

    if not l or not v:
        return ""

    li = _CHO_MAP.get(l)
    vi = _JUNG_MAP.get(v)
    ti = _JONG_MAP.get(t)

    if li is None or vi is None or ti is None:
        return ""

    s_base = 0xAC00
    v_count = 21
    t_count = 28

    codepoint = s_base + (li * v_count + vi) * t_count + ti
    try:
        return chr(codepoint)
    except Exception:
        return ""


def compose_cv(lead: str, vowel: str) -> str:
    """Compose a Hangul syllable from a leading consonant and a vowel."""
    return compose_lvt(lead, vowel, "")
