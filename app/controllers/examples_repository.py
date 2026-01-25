from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ExampleItem:
    hangul: str
    rr: str
    gloss_en: str
    category: str
    image_prompt: str
    starts_with_syllable: str
    starts_with_consonant: str
    starts_with_vowel: str
    image_filename: str | None = None


class ExamplesRepository:
    """Load and index example items from data/examples.yaml."""

    def __init__(self, *, data_path: Path | None = None) -> None:
        self._data_path = data_path or (Path(__file__).resolve().parents[2] / "data" / "examples.yaml")
        self._items: list[ExampleItem] = []
        self._by_syllable: dict[str, list[ExampleItem]] = {}
        self._by_consonant: dict[str, list[ExampleItem]] = {}
        self._by_vowel: dict[str, list[ExampleItem]] = {}

        self._load()

    @property
    def items(self) -> list[ExampleItem]:
        return list(self._items)

    def by_syllable(self, syllable: str) -> list[ExampleItem]:
        return list(self._by_syllable.get(syllable, []))

    def by_consonant(self, consonant: str) -> list[ExampleItem]:
        return list(self._by_consonant.get(consonant, []))

    def by_vowel(self, vowel: str) -> list[ExampleItem]:
        return list(self._by_vowel.get(vowel, []))

    def _load(self) -> None:
        data = self._read_yaml()
        items = data.get("examples", []) if isinstance(data, dict) else []
        for raw in items:
            item = self._parse_item(raw)
            if item is None:
                continue
            self._items.append(item)
            self._index(item)

    def _read_yaml(self) -> dict[str, Any]:
        try:
            if not self._data_path.exists():
                return {}
            raw = self._data_path.read_text(encoding="utf-8")
            data = yaml.safe_load(raw)
            return data if isinstance(data, dict) else {}
        except Exception:
            return {}

    def _parse_item(self, raw: Any) -> ExampleItem | None:
        if not isinstance(raw, dict):
            return None

        required = [
            "hangul",
            "rr",
            "gloss_en",
            "category",
            "image_prompt",
            "starts_with_syllable",
            "starts_with_consonant",
            "starts_with_vowel",
        ]
        for key in required:
            value = raw.get(key)
            if not isinstance(value, str) or not value.strip():
                return None

        return ExampleItem(
            hangul=raw["hangul"].strip(),
            rr=raw["rr"].strip(),
            gloss_en=raw["gloss_en"].strip(),
            category=raw["category"].strip(),
            image_prompt=raw["image_prompt"].strip(),
            starts_with_syllable=raw["starts_with_syllable"].strip(),
            starts_with_consonant=raw["starts_with_consonant"].strip(),
            starts_with_vowel=raw["starts_with_vowel"].strip(),
            image_filename=self._optional_str(raw.get("image_filename")),
        )

    def _index(self, item: ExampleItem) -> None:
        self._by_syllable.setdefault(item.starts_with_syllable, []).append(item)
        self._by_consonant.setdefault(item.starts_with_consonant, []).append(item)
        self._by_vowel.setdefault(item.starts_with_vowel, []).append(item)

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if isinstance(value, str):
            s = value.strip()
            return s if s else None
        return None
