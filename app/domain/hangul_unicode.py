

from __future__ import annotations

"""Hangul Unicode composition helpers.

This module is *domain* logic (no Qt dependencies).

It provides:
  - The canonical Unicode jamo tables for initial consonants (choseong) and vowels (jungsung)
  - `compose_cv()` for composing a Hangul syllable from a (lead consonant, vowel) pair.

Notes:
  - This is intentionally NOT the pedagogical ordering used for progression; that lives in
    `app/domain/jamo_data.py`.
"""

from typing import Final


# Unicode Hangul syllable constants
_HANGUL_BASE: Final[int] = 0xAC00

# Initial consonants (Choseong) for Unicode composition
_CHOESONG: Final[list[str]] = [
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"
]

# Medial vowels (Jungsung) for Unicode composition
_JUNGSUNG: Final[list[str]] = [
    "ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ",
    "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ",
]

# Lookup tables for fast composition
_DEF_L: Final[dict[str, int]] = {ch: i for i, ch in enumerate(_CHOESONG)}
_DEF_V: Final[dict[str, int]] = {ch: i for i, ch in enumerate(_JUNGSUNG)}


def compose_cv(lead: str, vowel: str) -> str:
    """Compose a Hangul syllable from a (lead consonant, vowel) pair.

    Args:
        lead: Leading consonant jamo (e.g., "ㄱ")
        vowel: Vowel jamo (e.g., "ㅏ")

    Returns:
        The composed Hangul syllable (e.g., "가").

    Raises:
        ValueError: if `lead` or `vowel` are not valid jamo for Unicode composition.
    """
    li = _DEF_L.get(str(lead))
    vi = _DEF_V.get(str(vowel))
    if li is None or vi is None:
        raise ValueError("Invalid jamo for compose_cv: lead=%r vowel=%r" % (lead, vowel))

    codepoint = _HANGUL_BASE + (li * 21 + vi) * 28
    try:
        return chr(codepoint)
    except Exception as e:
        raise ValueError("Unable to compose Hangul syllable for lead=%r vowel=%r" % (lead, vowel)) from e