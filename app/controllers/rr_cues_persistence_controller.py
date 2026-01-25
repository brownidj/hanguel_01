from __future__ import annotations

from PyQt6.QtWidgets import QRadioButton

from app.services.settings_store import SettingsStore


class RrCuesPersistenceController:
    """Persist RR cue visibility and restore on startup."""

    def __init__(self, *, radio: QRadioButton, settings_store: SettingsStore) -> None:
        self._radio = radio
        self._store = settings_store

    def wire(self) -> None:
        saved = self._store.get_rr_cues()
        if saved is not None:
            self._radio.setChecked(bool(saved))
        self._radio.toggled.connect(self._store.set_rr_cues)
