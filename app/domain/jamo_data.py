from __future__ import annotations

from pathlib import Path
from typing import Any, Final

import yaml


# ---------------------------------------------------------------------
# Defaults (used if YAML is missing or malformed)
# ---------------------------------------------------------------------

# Match the existing app behaviour (previously in main.py)
_DEFAULT_CONSONANTS: Final[tuple[str, ...]] = (
    "ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ",
    "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ",
)

# The app currently uses a “basic 10” list for progression
_DEFAULT_VOWELS_BASIC10: Final[tuple[str, ...]] = (
    "ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅡ", "ㅣ",
)

# Optional extended vowels (safe defaults; can be overridden by YAML)
_DEFAULT_VOWELS_ADVANCED: Final[tuple[str, ...]] = (
    "ㅐ", "ㅔ", "ㅒ", "ㅖ",
    "ㅘ", "ㅙ", "ㅚ",
    "ㅝ", "ㅞ", "ㅟ",
    "ㅢ",
)


# ---------------------------------------------------------------------
# YAML loading
# ---------------------------------------------------------------------

_YAML_CACHE: dict[str, Any] | None = None
_YAML_CACHE_PATH: Path | None = None
_YAML_CACHE_MTIME_NS: int | None = None


def _project_root() -> Path:
    # app/domain/jamo_data.py -> app/domain -> app -> <project_root>
    return Path(__file__).resolve().parents[2]


def _load_yaml() -> dict[str, Any]:
    """Load jamo ordering YAML if present.

    Failure is non-fatal; defaults will be used.

    Expected file: data/jamo_order.yaml
    """
    global _YAML_CACHE, _YAML_CACHE_PATH, _YAML_CACHE_MTIME_NS

    try:
        path = _project_root() / "data" / "jamo_order.yaml"
        if not path.exists():
            _YAML_CACHE = {}
            _YAML_CACHE_PATH = path
            _YAML_CACHE_MTIME_NS = None
            return {}

        mtime_ns = path.stat().st_mtime_ns
        if _YAML_CACHE is not None and _YAML_CACHE_PATH == path and _YAML_CACHE_MTIME_NS == mtime_ns:
            return dict(_YAML_CACHE)

        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            parsed = data if isinstance(data, dict) else {}

        _YAML_CACHE = dict(parsed)
        _YAML_CACHE_PATH = path
        _YAML_CACHE_MTIME_NS = mtime_ns
        return dict(_YAML_CACHE)
    except Exception:
        return {}


# ---------------------------------------------------------------------
# Public API (domain-level)
# ---------------------------------------------------------------------

def get_consonant_order() -> list[str]:
    """Return the ordered list of consonants for progression."""
    data = _load_yaml()
    consonants = data.get("consonants")
    if isinstance(consonants, list) and all(isinstance(c, str) for c in consonants):
        return list(consonants)
    return list(_DEFAULT_CONSONANTS)


def get_vowel_order_basic10() -> list[str]:
    """Return the ordered ‘basic 10’ vowel list used by the app."""
    data = _load_yaml()

    # Preferred: a dedicated key
    basic10 = data.get("vowels_basic10")
    if isinstance(basic10, list) and all(isinstance(v, str) for v in basic10):
        cleaned = [v.strip() for v in basic10 if v.strip()]
        if len(cleaned) == 10:
            return cleaned

    vowels = data.get("vowels")

    # Backward-compatible: a flat list meaning "basic10"
    if isinstance(vowels, list) and all(isinstance(v, str) for v in vowels):
        cleaned = [v.strip() for v in vowels if v.strip()]
        if len(cleaned) == 10:
            return cleaned

    # Backward-compatible: mapping with `basic10`
    if isinstance(vowels, dict):
        basic10 = vowels.get("basic10")
        if isinstance(basic10, list) and all(isinstance(v, str) for v in basic10):
            cleaned = [v.strip() for v in basic10 if v.strip()]
            if len(cleaned) == 10:
                return cleaned

    return list(_DEFAULT_VOWELS_BASIC10)


def get_vowel_order_advanced() -> list[str]:
    """Return the advanced/extended vowel list (used only when enabled)."""
    data = _load_yaml()
    vowels = data.get("vowels")
    if isinstance(vowels, dict):
        advanced = vowels.get("advanced")
        if isinstance(advanced, list) and all(isinstance(v, str) for v in advanced):
            cleaned = [v.strip() for v in advanced if v.strip()]
            return cleaned
    return list(_DEFAULT_VOWELS_ADVANCED)


# Public domain-data defaults (use the getters for YAML-backed values)
DEFAULT_CONSONANT_ORDER: Final[tuple[str, ...]] = _DEFAULT_CONSONANTS
DEFAULT_VOWEL_ORDER_BASIC10: Final[tuple[str, ...]] = _DEFAULT_VOWELS_BASIC10
DEFAULT_VOWEL_ORDER_ADVANCED: Final[tuple[str, ...]] = _DEFAULT_VOWELS_ADVANCED