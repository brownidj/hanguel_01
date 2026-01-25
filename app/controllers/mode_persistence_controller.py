from __future__ import annotations

from PyQt6.QtWidgets import QComboBox

from app.services.settings_store import SettingsStore


class ModePersistenceController:
    """Persist mode changes and restore on startup."""

    def __init__(self, *, combo: QComboBox, settings_store: SettingsStore) -> None:
        self._combo = combo
        self._store = settings_store

    def wire(self) -> None:
        saved = self._store.get_mode()
        if saved:
            idx = self._combo.findText(saved)
            if idx >= 0:
                self._combo.setCurrentIndex(idx)
        self._combo.currentTextChanged.connect(self._store.set_mode)
