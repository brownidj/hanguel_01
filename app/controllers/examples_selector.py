from __future__ import annotations

from typing import Callable

from app.controllers.examples_repository import ExampleItem, ExamplesRepository
from app.domain.hangul_compose import compose_cv


class ExamplesSelector:
    """Deterministic example selector for the current study item."""

    def __init__(
        self,
        *,
        get_mode_text: Callable[[], str],
        get_current_pair: Callable[[], tuple[str, str]],
        get_current_index: Callable[[], int],
        repository: ExamplesRepository,
    ) -> None:
        self._get_mode_text = get_mode_text
        self._get_current_pair = get_current_pair
        self._get_current_index = get_current_index
        self._repo = repository

    def pick_example(self, *, offset: int = 0) -> ExampleItem | None:
        mode = (self._get_mode_text() or "").strip().lower()
        consonant, vowel = self._get_current_pair()
        syllable = compose_cv(consonant, vowel) or ""

        if mode == "vowels":
            candidates = [item for item in self._repo.by_vowel(vowel) if item.starts_with_consonant == "ㅇ"]
            if not candidates:
                candidates = self._repo.by_vowel(vowel)
            return self._pick_from_candidates(candidates, key=vowel, offset=offset)
        if mode == "consonants":
            candidates = self._repo.by_consonant(consonant)
            return self._pick_from_candidates(candidates, key=consonant, offset=offset)

        candidates = self._repo.by_syllable(syllable)
        if candidates:
            return self._pick_from_candidates(candidates, key=syllable, offset=offset)

        candidates = self._repo.by_consonant(consonant)
        if candidates:
            return self._pick_from_candidates(candidates, key=consonant, offset=offset)

        candidates = self._repo.by_vowel(vowel)
        return self._pick_from_candidates(candidates, key=vowel, offset=offset)

    def _pick_from_candidates(
        self,
        candidates: list[ExampleItem],
        *,
        key: str,
        offset: int,
    ) -> ExampleItem | None:
        if not candidates:
            return None
        base_index = int(self._get_current_index())
        key_weight = sum(ord(ch) for ch in (key or ""))
        idx = (base_index + key_weight + int(offset)) % len(candidates)
        return candidates[idx]
