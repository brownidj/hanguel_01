from __future__ import annotations

import os
from typing import Callable

from PyQt6.QtWidgets import QLabel, QStackedWidget

from app.controllers.block_manager import BlockManager
from app.controllers.syllable_navigation import SyllableNavigation


class NavigationController:
    """Owns study-item navigation + rendering for the main content area."""

    def __init__(
        self,
        *,
        nav: SyllableNavigation,
        block_manager: BlockManager,
        stacked: QStackedWidget,
        syllable_label: QLabel | None,
        get_mode_text: Callable[[], str],
        compose_cv: Callable[[str, str], str],
    ) -> None:
        self._nav = nav
        self._block_manager = block_manager
        self._stacked = stacked
        self._syllable_label = syllable_label
        self._get_mode_text = get_mode_text
        self._compose_cv = compose_cv
        self._on_item_changed: list[Callable[[], None]] = []

    def set_on_item_changed(self, callback: Callable[[], None] | None) -> None:
        self._on_item_changed = []
        if callback is not None:
            self._on_item_changed.append(callback)

    def add_on_item_changed(self, callback: Callable[[], None] | None) -> None:
        if callback is None:
            return
        self._on_item_changed.append(callback)

    def current_pair(self) -> tuple[str, str]:
        return self._nav.current_pair()

    def current_glyph(self) -> str:
        if self._syllable_label is not None:
            try:
                text = (self._syllable_label.text() or "").strip()
                if text:
                    return text
            except Exception:
                pass
        consonant, vowel = self._nav.current_pair()
        return self._compose_cv(consonant, vowel) or ""

    def on_mode_changed(self, mode_text: str) -> None:
        self._nav.reload_for_mode(mode_text, reset_index=True)
        self.render_current()

    def advance(self, delta: int) -> None:
        self._nav.advance(int(delta), mode_text=self._get_mode_text())
        self.render_current()

    def go_next(self) -> None:
        self.advance(+1)

    def go_prev(self) -> None:
        self.advance(-1)

    def render_current(self) -> None:
        try:
            mode_text = self._get_mode_text().strip().lower()
            consonant, vowel = self._nav.current_pair()
            if str(os.environ.get("HANGUL_DEBUG_RENDER", "")).strip().lower() in ("1", "true", "yes", "on"):
                try:
                    print("[DEBUG] Syllable render pair: {} {}".format(consonant, vowel))
                except Exception:
                    pass
            if mode_text == "consonants":
                self._block_manager.show_consonant(
                    stacked=self._stacked,
                    consonant=consonant,
                    syll_label=self._syllable_label,
                    type_label=None,
                )
                self._notify_item_changed()
                return
            if mode_text == "vowels":
                self._block_manager.show_pair(
                    stacked=self._stacked,
                    consonant="ㅇ",
                    vowel=vowel,
                    syll_label=self._syllable_label,
                    type_label=None,
                )
                self._notify_item_changed()
                return
            self._block_manager.show_pair(
                stacked=self._stacked,
                consonant=consonant,
                vowel=vowel,
                syll_label=self._syllable_label,
                type_label=None,
            )
            self._notify_item_changed()
        except (AttributeError, RuntimeError, TypeError):
            return

    def _notify_item_changed(self) -> None:
        if not self._on_item_changed:
            return
        for cb in list(self._on_item_changed):
            try:
                cb()
            except Exception:
                pass
