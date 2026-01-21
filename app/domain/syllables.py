from __future__ import annotations

"""Syllable data access (domain layer).

This module is intentionally Qt-free.

Responsibilities:
- Resolve the project root in a stable way.
- Load syllable data from YAML (if present).
- Select a representative syllable for a given BlockType.

Expected YAML location:
- data/syllables.yaml

Expected YAML shape (flexible):
- Either a mapping keyed by full block type names (e.g., "A_RightBranch") to a list of syllables
- Or a mapping keyed by short letters ("A", "B", "C", "D") to a list of syllables
"""

from pathlib import Path
from typing import Any, Final


# -----------------------------------------------------------------------------
# Cache
# -----------------------------------------------------------------------------

_YAML_CACHE: dict[str, Any] | None = None
_YAML_CACHE_PATH: Path | None = None
_YAML_CACHE_MTIME_NS: int | None = None

_SYLLABLES_FILENAME: Final[str] = "syllables.yaml"


# -----------------------------------------------------------------------------
# Path helpers
# -----------------------------------------------------------------------------

def _project_root() -> Path:
    """Return the project root directory.

    Assumes this file lives at: <root>/app/domain/syllables.py
    so we walk up two levels.
    """
    try:
        return Path(__file__).resolve().parents[2]
    except Exception:
        return Path.cwd()


def _syllables_yaml_path() -> Path:
    return _project_root() / "data" / _SYLLABLES_FILENAME


# -----------------------------------------------------------------------------
# YAML loading
# -----------------------------------------------------------------------------

def _load_syllables_yaml() -> dict[str, Any]:
    """Load syllables YAML if present.

    Failure is non-fatal; returns an empty mapping.
    Uses a small mtime-based cache to avoid repeated disk reads.
    """
    global _YAML_CACHE, _YAML_CACHE_PATH, _YAML_CACHE_MTIME_NS

    try:
        path = _syllables_yaml_path()
        if not path.exists():
            _YAML_CACHE = {}
            _YAML_CACHE_PATH = path
            _YAML_CACHE_MTIME_NS = None
            return {}

        mtime_ns = path.stat().st_mtime_ns
        if _YAML_CACHE is not None and _YAML_CACHE_PATH == path and _YAML_CACHE_MTIME_NS == mtime_ns:
            return dict(_YAML_CACHE)

        import yaml

        with path.open("r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            parsed = loaded if isinstance(loaded, dict) else {}

        _YAML_CACHE = dict(parsed)
        _YAML_CACHE_PATH = path
        _YAML_CACHE_MTIME_NS = mtime_ns
        return dict(_YAML_CACHE)
    except Exception:
        return {}


# -----------------------------------------------------------------------------
# Selection
# -----------------------------------------------------------------------------

def _normalise_key(block: object) -> tuple[str, str]:
    """Return (full_name, short_letter) keys for lookup."""
    name = getattr(block, "name", None)
    full = str(name) if name else str(block)
    short = full[:1] if full else ""
    return full, short


def select_syllable_for_block(block_type: object) -> str:
    """Return a representative syllable for the given BlockType.

    Best-effort and conservative:
    - If YAML provides candidates, returns the first non-empty string.
    - Otherwise returns a stable fallback per block group.
    """
    data = _load_syllables_yaml()
    full, short = _normalise_key(block_type)

    candidates: Any = None

    # Preferred: full enum name keys
    if full and full in data:
        candidates = data.get(full)

    # Fallback: A/B/C/D keys
    if candidates is None and short and short in data:
        candidates = data.get(short)

    if isinstance(candidates, list):
        for s in candidates:
            if isinstance(s, str):
                cleaned = s.strip()
                if cleaned:
                    return cleaned

    # Stable, conservative fallbacks (one per block family)
    if short == "A":
        return "가"
    if short == "B":
        return "고"
    if short == "C":
        return "구"
    if short == "D":
        return "그"

    return "가"
