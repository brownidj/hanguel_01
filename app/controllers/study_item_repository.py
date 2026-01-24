from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


def _default_data_dir() -> Path:
    """Return the project-root data directory.

    Assumes this file lives at: <root>/app/controllers/study_item_repository.py
    """
    return Path(__file__).resolve().parents[2] / "data"


@dataclass(frozen=True)
class StudyItemRepository:
    """Load practice items (syllables/vowels/consonants) from YAML files.

    The repository returns items as pairs `(consonant, vowel)`.

    Supported YAML shapes (intentionally tolerant):

    1) A list of strings
        - syllables: ["ㄱㅏ", "ㄴㅏ", ...]
        - vowels:   ["ㅏ", "ㅑ", ...]
        - consonants:["ㄱ", "ㄴ", ...]

    2) A dict containing a list under a common key
        - {syllables: [...]} or {items: [...]} or {vowels: [...]} etc.

    3) A list of dict items
        - syllables: [{c: "ㄱ", v: "ㅏ"}, {consonant: "ㄴ", vowel: "ㅏ"}, ...]
        - vowels:    [{v: "ㅏ"}, {vowel: "ㅑ"}, ...]
        - consonants:[{c: "ㄱ"}, {consonant: "ㄴ"}, ...]

    Notes:
    - For syllables, entries may be compact CV strings like "ㄱㅏ".
    - For syllables, entries may also be a single precomposed Hangul syllable (e.g. "가").
      If so, we decompose it to (compatibility choseong, compatibility jungseong).
    """

    project_root: Path | None = None

    @property
    def data_dir(self) -> Path:
        if self.project_root is not None:
            return self.project_root / "data"
        return _default_data_dir()

    ''' Compatibility jamo lookup tables for Hangul syllable decomposition.
    We return compatibility jamo because the UI and YAMLs typically use them. Those tables 
    are hard-coded because they are the fixed Unicode mapping needed to convert precomposed 
    Hangul syllables into the exact compatibility jamo glyphs your UI, YAML data, 
    and tests are built around, and treating them as configurable data would be both 
    incorrect and fragile.
    '''

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

    def _read_yaml(self, filename: str) -> Any:
        path = self.data_dir / filename
        if not path.exists() or not path.is_file():
            return None

        try:
            raw = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            return None

        try:
            return yaml.safe_load(raw)
        except yaml.YAMLError:
            return None

    @staticmethod
    def _as_nonempty_str(value: Any) -> str | None:
        if isinstance(value, str):
            s = value.strip()
            return s if s else None
        return None

    @classmethod
    def _pick_str(cls, mapping: Any, keys: Iterable[str]) -> str | None:
        if not isinstance(mapping, dict):
            return None
        for k in keys:
            v = mapping.get(k)
            s = cls._as_nonempty_str(v)
            if s is not None:
                return s
        return None

    @staticmethod
    def _iter_items(container: Any, preferred_keys: Iterable[str]) -> list[Any]:
        """Return a list of items from either a list or a dict wrapper."""
        if isinstance(container, list):
            return container

        if isinstance(container, dict):
            # common wrappers
            for k in preferred_keys:
                v = container.get(k)
                if isinstance(v, list):
                    return v
            # fall back to very common generic keys
            for k in ("items", "data", "list"):
                v = container.get(k)
                if isinstance(v, list):
                    return v

        return []

    def _decompose_precomposed_syllable(self, s: str) -> tuple[str, str] | None:
        """If `s` is a single precomposed Hangul syllable, return (C, V) in compatibility jamo."""
        if len(s) != 1:
            return None
        code = ord(s)
        # Hangul syllables: AC00..D7A3
        if code < 0xAC00 or code > 0xD7A3:
            return None

        syllable_index = code - 0xAC00
        cho_index = syllable_index // 588
        jung_index = (syllable_index % 588) // 28

        if 0 <= cho_index < len(self._COMPAT_CHO) and 0 <= jung_index < len(self._COMPAT_JUNG):
            return self._COMPAT_CHO[cho_index], self._COMPAT_JUNG[jung_index]

        return None

    def _load_syllable_pairs(self) -> list[tuple[str, str]]:
        data = self._read_yaml("syllables.yaml")
        items = self._iter_items(data, preferred_keys=("syllables", "syllable", "cv", "pairs"))

        pairs: list[tuple[str, str]] = []
        for item in items:
            # Case 1: plain string
            s = self._as_nonempty_str(item)
            if s is not None:
                # "ㄱㅏ" style
                if len(s) >= 2:
                    pairs.append((s[0], s[1]))
                    continue
                # "가" style
                decomposed = self._decompose_precomposed_syllable(s)
                if decomposed is not None:
                    pairs.append(decomposed)
                continue

            # Case 2: dict-style item
            if isinstance(item, dict):
                c = self._pick_str(item, ("c", "consonant", "onset", "initial", "cho"))
                v = self._pick_str(item, ("v", "vowel", "nucleus", "medial", "jung"))

                if c is not None and v is not None:
                    pairs.append((c, v))
                    continue

                # Maybe the item stores a compact field
                cv = self._pick_str(item, ("cv", "text", "value", "syllable"))
                if cv is not None:
                    if len(cv) >= 2:
                        pairs.append((cv[0], cv[1]))
                        continue
                    decomposed = self._decompose_precomposed_syllable(cv)
                    if decomposed is not None:
                        pairs.append(decomposed)
        # Fallback if no pairs loaded
        if not pairs:
            return [("ㄱ", "ㅏ")]
        return pairs

    def _load_vowel_pairs(self) -> list[tuple[str, str]]:
        data = self._read_yaml("vowels.yaml")
        items = self._iter_items(data, preferred_keys=("vowels", "vowel"))

        out: list[tuple[str, str]] = []
        for item in items:
            s = self._as_nonempty_str(item)
            if s is not None:
                out.append(("∅", s))
                continue
            if isinstance(item, dict):
                v = self._pick_str(item, ("v", "vowel", "glyph", "text", "value"))
                if v is not None:
                    out.append(("∅", v))
        if not out:
            return [("∅", "ㅏ")]
        return out

    def _load_consonant_pairs(self) -> list[tuple[str, str]]:
        data = self._read_yaml("consonants.yaml")
        items = self._iter_items(data, preferred_keys=("consonants", "consonant"))

        out: list[tuple[str, str]] = []
        for item in items:
            s = self._as_nonempty_str(item)
            if s is not None:
                out.append((s, "∅"))
                continue
            if isinstance(item, dict):
                c = self._pick_str(item, ("c", "consonant", "glyph", "text", "value"))
                if c is not None:
                    out.append((c, "∅"))
        if not out:
            return [("ㄱ", "∅")]
        return out

    # --- Public API (used by controller/tests) ---

    def syllable_pairs(self) -> list[tuple[str, str]]:
        return self._load_syllable_pairs()

    def vowel_pairs(self) -> list[tuple[str, str]]:
        return self._load_vowel_pairs()

    def consonant_pairs(self) -> list[tuple[str, str]]:
        return self._load_consonant_pairs()

    def pairs_for_mode(self, mode_text: str) -> list[tuple[str, str]]:
        """Return pairs for UI mode text: 'Syllables', 'Vowels', 'Consonants'."""
        m = (mode_text or "").strip().lower()
        if m == "vowels":
            return self.vowel_pairs()
        if m == "consonants":
            return self.consonant_pairs()
        return self.syllable_pairs()