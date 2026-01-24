from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from PyQt6.QtWidgets import QComboBox

logger = logging.getLogger(__name__)


@dataclass
class ModeController:
    """Owns the Mode combobox wiring.

    Responsibilities:
    - listen for mode changes (Syllables / Vowels / Consonants)
    - forward the selected mode text to an injected handler

    This class does not implement navigation or rendering itself.
    """

    combo: QComboBox
    on_mode_changed: Callable[[str], None]

    def wire(self) -> None:
        """Attach Qt signal handlers (idempotent best-effort)."""
        if self.combo is None:
            return

        # Avoid duplicate connections if wire() is called more than once.
        try:
            try:
                self.combo.currentTextChanged.disconnect()  # type: ignore[arg-type]
            except (TypeError, RuntimeError):
                # Not connected (or combo already deleted)
                pass

            self.combo.currentTextChanged.connect(self._on_text_changed)
        except (AttributeError, RuntimeError):
            return

    def _on_text_changed(self, text: str) -> None:
        try:
            self.on_mode_changed(text)
        except (AttributeError, RuntimeError, TypeError):
            # Handler is injected; keep UI resilient.
            try:
                logger.exception("ModeController handler failed")
            except (AttributeError, RuntimeError):
                pass