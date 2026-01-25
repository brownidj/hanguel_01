from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

_CACHE: dict[str, dict[str, dict[str, str]]] = {}
_CACHE_MTIME_NS: dict[str, int] = {}


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _load_yaml(name: str) -> dict[str, Any]:
    path = _project_root() / "data" / name
    try:
        if not path.exists():
            return {}
        mtime_ns = path.stat().st_mtime_ns
        cache_key = str(path)
        if cache_key in _CACHE and _CACHE_MTIME_NS.get(cache_key) == mtime_ns:
            return _CACHE[cache_key]
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        parsed = data if isinstance(data, dict) else {}
        _CACHE[cache_key] = parsed
        _CACHE_MTIME_NS[cache_key] = mtime_ns
        return parsed
    except Exception:
        return {}


def _extract_rr_map(data: dict[str, Any], key: str) -> dict[str, dict[str, str]]:
    out: dict[str, dict[str, str]] = {}
    items = data.get(key)
    if not isinstance(items, list):
        return out
    for item in items:
        if not isinstance(item, dict):
            continue
        glyph = item.get("glyph")
        rr = item.get("rr")
        if isinstance(glyph, str) and isinstance(rr, dict):
            cleaned = {k: str(v) for k, v in rr.items() if isinstance(k, str)}
            out[glyph] = cleaned
    return out


def consonant_rr(glyph: str) -> dict[str, str]:
    data = _load_yaml("consonants.yaml")
    return _extract_rr_map(data, "consonants").get(glyph, {})


def vowel_rr(glyph: str) -> dict[str, str]:
    data = _load_yaml("vowels.yaml")
    return _extract_rr_map(data, "vowels").get(glyph, {})
