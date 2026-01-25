from __future__ import annotations

import logging
from dataclasses import dataclass, field

from app.controllers.study_item_repository import StudyItemRepository

logger = logging.getLogger(__name__)


@dataclass
class SyllableNavigation:
    """YAML-backed study-item navigation.

    Owns:
    - active list of (consonant, vowel) pairs for the current mode
    - current index into that list
    - current (consonant, vowel)

    The controller remains responsible for rendering.
    """

    repo: StudyItemRepository
    pairs: list[tuple[str, str]] = field(default_factory=list)
    index: int = 0
    current_consonant: str = "ㄱ"
    current_vowel: str = "ㅏ"

    def reload_for_mode(self, mode_text: str, *, reset_index: bool) -> None:
        """Reload pairs from repository for a mode label (Syllables/Vowels/Consonants)."""
        try:
            self.pairs = self.repo.pairs_for_mode(mode_text)
        except Exception as e:
            try:
                logger.debug("SyllableNavigation.reload_for_mode failed: %s", e)
            except Exception:
                pass
            self.pairs = []

        if reset_index:
            self.index = 0

        if self.pairs:
            self.current_consonant, self.current_vowel = self.pairs[self.index]
        else:
            # Safe fallback; UI will still render placeholder glyphs.
            self.current_consonant = "ㄱ"
            self.current_vowel = "ㅏ"

    def ensure_loaded(self, mode_text: str) -> None:
        """Ensure `pairs` is loaded (best-effort) using the provided mode text."""
        if not self.pairs:
            self.reload_for_mode(mode_text, reset_index=True)

    def advance(self, delta: int, *, mode_text: str) -> tuple[str, str]:
        """Advance by `delta` (wraparound) and return the new (consonant, vowel)."""
        self.ensure_loaded(mode_text)
        if not self.pairs:
            return self.current_consonant, self.current_vowel

        self.index = (self.index + int(delta)) % len(self.pairs)
        self.current_consonant, self.current_vowel = self.pairs[self.index]
        return self.current_consonant, self.current_vowel

    def current_pair(self) -> tuple[str, str]:
        return self.current_consonant, self.current_vowel

    def current_index(self) -> int:
        return int(self.index)
