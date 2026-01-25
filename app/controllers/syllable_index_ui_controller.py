from __future__ import annotations

from typing import Callable

from PyQt6.QtWidgets import QLabel, QWidget

from app.controllers.syllable_navigation import SyllableNavigation
from app.ui.utils.qt_find import find_child


class SyllableIndexUiController:
    """Owns the index/total indicator for the current mode list."""

    def __init__(
        self,
        *,
        window: QWidget,
        navigation: SyllableNavigation,
        get_mode_text: Callable[[], str],
        label_name: str = "labelSyllableIndex",
    ) -> None:
        self._window = window
        self._navigation = navigation
        self._get_mode_text = get_mode_text
        self._label_name = label_name
        self._label: QLabel | None = None

    def wire(self) -> None:
        self._label = find_child(self._window, QLabel, self._label_name)
        if self._label is None:
            return
        self.update()

    def update(self) -> None:
        if self._label is None:
            return
        try:
            self._navigation.ensure_loaded(self._get_mode_text())
            total = len(self._navigation.pairs)
            index = self._navigation.current_index() + 1 if total > 0 else 0
            self._label.setText(f"{index}/{total}")
        except Exception:
            self._label.setText("0/0")
