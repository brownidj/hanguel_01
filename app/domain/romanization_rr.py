from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class RRSegment:
    text: str
    role: str  # "consonant" | "vowel" | "final" (future)

@dataclass(frozen=True)
class RRResult:
    rr: str
    hint: str
    details: list[str]
    segments: list[RRSegment]


_VOWEL_RR: dict[str, str] = {
    "ㅏ": "a",
    "ㅓ": "eo",
    "ㅗ": "o",
    "ㅜ": "u",
    "ㅡ": "eu",
    "ㅣ": "i",
    "ㅐ": "ae",
    "ㅔ": "e",
    "ㅚ": "oe",
    "ㅟ": "wi",
    "ㅘ": "wa",
    "ㅝ": "wo",
    "ㅙ": "wae",
    "ㅞ": "we",
    "ㅢ": "ui",
    "ㅑ": "ya",
    "ㅕ": "yeo",
    "ㅛ": "yo",
    "ㅠ": "yu",
    "ㅒ": "yae",
    "ㅖ": "ye",
}

_CONS_RR: dict[str, str] = {
    "ㄱ": "g",
    "ㄴ": "n",
    "ㄷ": "d",
    "ㄹ": "r",
    "ㅁ": "m",
    "ㅂ": "b",
    "ㅅ": "s",
    "ㅇ": "",
    "ㅈ": "j",
    "ㅊ": "ch",
    "ㅋ": "k",
    "ㅌ": "t",
    "ㅍ": "p",
    "ㅎ": "h",
    "ㄲ": "kk",
    "ㄸ": "tt",
    "ㅃ": "pp",
    "ㅆ": "ss",
    "ㅉ": "jj",
}

_CONS_HINTS: dict[str, str] = {
    "ㄱ": "between g/k (unaspirated)",
    "ㄷ": "between d/t (unaspirated)",
    "ㅂ": "between b/p (unaspirated)",
    "ㄹ": "r/l (light tap)",
    "ㅅ": "s",
    "ㅇ": "silent at start",
    "ㅈ": "j (unaspirated)",
}

_VOWEL_HINTS: dict[str, str] = {
    "ㅏ": "a",
    "ㅓ": "eo (uh, more open)",
    "ㅗ": "o",
    "ㅜ": "u",
    "ㅡ": "eu (close to \"uh\")",
    "ㅣ": "i",
    "ㅐ": "ae",
    "ㅔ": "e",
    "ㅚ": "oe",
    "ㅟ": "wi",
    "ㅘ": "wa",
    "ㅝ": "wo",
    "ㅙ": "wae",
    "ㅞ": "we",
    "ㅢ": "ui",
    "ㅑ": "ya",
    "ㅕ": "yeo",
    "ㅛ": "yo",
    "ㅠ": "yu",
    "ㅒ": "yae",
    "ㅖ": "ye",
}

_CONS_EXAMPLES: dict[str, str] = {
    "ㄱ": "go",
    "ㄴ": "no",
    "ㄷ": "day",
    "ㄹ": "ladder",
    "ㅁ": "man",
    "ㅂ": "boy",
    "ㅅ": "see",
    "ㅈ": "jam",
    "ㅊ": "chat",
    "ㅋ": "kite",
    "ㅌ": "tea",
    "ㅍ": "pie",
    "ㅎ": "hat",
    "ㄲ": "skate",
    "ㄸ": "stop",
    "ㅃ": "spot",
    "ㅆ": "sea",
    "ㅉ": "jeep",
}

_VOWEL_EXAMPLES: dict[str, str] = {
    "ㅏ": "father",
    "ㅓ": "sun",
    "ㅗ": "go",
    "ㅜ": "food",
    "ㅡ": "sofa",
    "ㅣ": "see",
    "ㅐ": "cat",
    "ㅔ": "bed",
    "ㅚ": "way",
    "ㅟ": "we",
    "ㅘ": "waffle",
    "ㅝ": "wonder",
    "ㅙ": "wax",
    "ㅞ": "wet",
    "ㅢ": "we",
    "ㅑ": "yard",
    "ㅕ": "yawn",
    "ㅛ": "yoga",
    "ㅠ": "you",
    "ㅒ": "yeah",
    "ㅖ": "yes",
}

_S_LIKE_VOWELS: set[str] = {"ㅣ", "ㅑ", "ㅕ", "ㅛ", "ㅠ", "ㅖ", "ㅒ"}

_COMPAT_CHO: tuple[str, ...] = (
    "ㄱ",
    "ㄲ",
    "ㄴ",
    "ㄷ",
    "ㄸ",
    "ㄹ",
    "ㅁ",
    "ㅂ",
    "ㅃ",
    "ㅅ",
    "ㅆ",
    "ㅇ",
    "ㅈ",
    "ㅉ",
    "ㅊ",
    "ㅋ",
    "ㅌ",
    "ㅍ",
    "ㅎ",
)

_COMPAT_JUNG: tuple[str, ...] = (
    "ㅏ",
    "ㅐ",
    "ㅑ",
    "ㅒ",
    "ㅓ",
    "ㅔ",
    "ㅕ",
    "ㅖ",
    "ㅗ",
    "ㅘ",
    "ㅙ",
    "ㅚ",
    "ㅛ",
    "ㅜ",
    "ㅝ",
    "ㅞ",
    "ㅟ",
    "ㅠ",
    "ㅡ",
    "ㅢ",
    "ㅣ",
)


def romanize_cv(consonant: str, vowel: str, final: Optional[str] = None) -> RRResult:
    # Phase 1: tables + simple hints, ignore final
    cons = (consonant or "").strip()
    vow = (vowel or "").strip()

    if cons == "∅":
        cons = ""
    if vow == "∅":
        vow = ""

    cons_rr = _CONS_RR.get(cons, cons)
    vow_rr = _VOWEL_RR.get(vow, vow)
    rr = "{}{}".format(cons_rr, vow_rr)

    details: list[str] = []
    segments: list[RRSegment] = []

    if cons_rr:
        segments.append(RRSegment(text=cons_rr, role="consonant"))
    if vow_rr:
        segments.append(RRSegment(text=vow_rr, role="vowel"))

    if cons:
        cons_hint = _CONS_HINTS.get(cons, cons_rr or cons)
        if cons == "ㅅ" and vow in _S_LIKE_VOWELS:
            cons_hint = "s (can sound sh-like before i/y)"
        cons_example = _CONS_EXAMPLES.get(cons, "")
        if cons_example:
            details.append("{} = {}, as in '{}'".format(cons, cons_hint, cons_example))
        else:
            details.append("{} = {}".format(cons, cons_hint))
    if vow:
        vowel_hint = _VOWEL_HINTS.get(vow, vow_rr or vow)
        vowel_example = _VOWEL_EXAMPLES.get(vow, "")
        if vowel_example:
            details.append("{} = {}, as in '{}'".format(vow, vowel_hint, vowel_example))
        else:
            details.append("{} = {}".format(vow, vowel_hint))

    if details:
        hint = "; ".join(details)
    else:
        hint = rr

    return RRResult(
        rr=rr,
        hint=hint,
        details=details,
        segments=segments,
    )

def romanize_text(text: str) -> RRResult:
    if not text:
        return RRResult(rr="", hint="", details=[], segments=[])

    rr_parts: list[str] = []
    for ch in text:
        code = ord(ch)
        if 0xAC00 <= code <= 0xD7A3:
            idx = code - 0xAC00
            cho_index = idx // 588
            jung_index = (idx % 588) // 28
            if 0 <= cho_index < len(_COMPAT_CHO) and 0 <= jung_index < len(_COMPAT_JUNG):
                cons = _COMPAT_CHO[cho_index]
                vow = _COMPAT_JUNG[jung_index]
                rr_parts.append(romanize_cv(cons, vow).rr)
                continue
        rr_parts.append(ch)

    rr = "".join(rr_parts)
    details = [
        "RR spelling: {}".format(rr),
        "Pronunciation hint: {}".format(rr),
    ]
    hint = "\n".join(details)
    return RRResult(rr=rr, hint=hint, details=details, segments=[])
