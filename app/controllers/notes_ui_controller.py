from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtWidgets import QLabel, QGroupBox, QWidget

from app.domain.hangul_compose import compose_cv


class NotesUiController:
    """Owns Notes panel content updates."""

    def __init__(
        self,
        *,
        window: QWidget,
        get_mode_text: Callable[[], str],
        get_current_pair: Callable[[], tuple[str, str]],
    ) -> None:
        self._window = window
        self._get_mode_text = get_mode_text
        self._get_current_pair = get_current_pair
        self._label: Optional[QLabel] = None
        self._panel: Optional[QGroupBox] = None

    def wire(self) -> None:
        self._label = self._window.findChild(QLabel, "labelNotesPlaceholder")
        self._panel = self._window.findChild(QGroupBox, "groupNotesPanel")
        self.update()

    def update(self) -> None:
        if self._label is None:
            return
        mode = (self._get_mode_text() or "").strip().lower()
        if mode != "vowels":
            try:
                self._label.setText("")
                self._label.setVisible(False)
                if self._panel is not None:
                    self._panel.setVisible(False)
            except Exception:
                pass
            return
        consonant, vowel = self._get_current_pair()
        syllable = compose_cv("ㅇ", vowel) or ""
        text = (
            "Standalone vowels are written with a silent ㅇ onset, so {} is written as ㅇ{} (ㅇ + {})."
        ).format(vowel or "ㅏ", syllable or "아", vowel or "ㅏ")
        try:
            self._label.setText(text)
            self._label.setVisible(True)
            if self._panel is not None:
                self._panel.setVisible(True)
        except Exception:
            pass
