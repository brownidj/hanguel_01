from __future__ import annotations

from typing import Iterable, Optional

from PyQt6.QtWidgets import QComboBox, QWidget

from app.controllers.mode_controller import ModeController
from app.controllers.navigation_controller import NavigationController


class ModeUiController:
    """Owns mode combobox discovery and wiring to navigation."""

    def __init__(
        self,
        *,
        window: QWidget,
        navigation: NavigationController | None,
        combo_names: Optional[Iterable[str]] = None,
    ) -> None:
        self._window = window
        self._navigation = navigation
        self._combo_names = list(combo_names or ["comboMode", "comboStudyMode", "comboBoxMode"])
        self.combo: QComboBox | None = None
        self._mode_controller: ModeController | None = None

    def wire(self) -> None:
        if self._navigation is None:
            return
        self.combo = self._find_combo()
        if self.combo is None:
            return
        self._mode_controller = ModeController(self.combo, self._navigation.on_mode_changed)
        self._mode_controller.wire()

    def current_text(self) -> str:
        mode_text = "Syllables"
        if self.combo is None:
            return mode_text
        try:
            return self.combo.currentText() or mode_text
        except (AttributeError, RuntimeError):
            return mode_text

    def _find_combo(self) -> QComboBox | None:
        for name in self._combo_names:
            combo = self._window.findChild(QComboBox, name)
            if isinstance(combo, QComboBox):
                return combo
        return None
