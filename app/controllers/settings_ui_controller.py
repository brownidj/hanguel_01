from __future__ import annotations

from typing import Any, Optional

from PyQt6.QtWidgets import QDoubleSpinBox, QSpinBox, QWidget

from app.controllers.pronunciation_controller import PronunciationController
from app.controllers.settings_controller import SettingsController
from app.controllers.wpm_controller import WpmController
from app.services.settings_store import SettingsStore


class SettingsUiController:
    """Owns settings UI wiring (spinboxes + persistence)."""

    def __init__(self, *, window: QWidget, settings_store: SettingsStore) -> None:
        self._window = window
        self._store = settings_store
        self._settings_controller = SettingsController(settings_store)
        self._wpm_controller = WpmController(
            window=window,
            pronouncer=None,
            settings_store=settings_store,
        )

    @property
    def settings_controller(self) -> SettingsController:
        return self._settings_controller

    @property
    def wpm_controller(self) -> WpmController:
        return self._wpm_controller

    def set_pronouncer(self, pronouncer: Optional[PronunciationController]) -> None:
        self._wpm_controller.set_pronouncer(pronouncer)

    def wire(self) -> None:
        spin_repeats = self._window.findChild(QSpinBox, "spinRepeats")
        spin_pre_first = self._window.findChild(QSpinBox, "spinDelayPreFirst")
        spin_between = self._window.findChild(QSpinBox, "spinDelayBetweenReps")
        spin_before_hints = self._window.findChild(QSpinBox, "spinDelayBeforeHints")
        spin_before_extras = self._window.findChild(QSpinBox, "spinDelayBeforeExtras")
        spin_auto_advance = self._window.findChild(QDoubleSpinBox, "spinDelayAutoAdvance")

        self._settings_controller.bind_repeats_spinbox(spin_repeats)
        self._settings_controller.bind_delay_spinboxes(
            spin_pre_first=spin_pre_first,
            spin_between_reps=spin_between,
            spin_before_hints=spin_before_hints,
            spin_before_extras=spin_before_extras,
            spin_auto_advance=spin_auto_advance,
        )
        self._settings_controller.apply_repeats_from_store()
        self._settings_controller.apply_delays_from_store()
        self._settings_controller.wire_repeats_persistence()
        self._settings_controller.wire_delay_persistence()
        self._wpm_controller.wire_wpm_controls()
        self._wpm_controller.init_slow_chip()

    def apply_persisted_settings(self) -> None:
        data = self._store.load() or {}

        repeats = data.get("repeats")
        delays = data.get("delays", {}) if isinstance(data.get("delays", {}), dict) else {}

        def _set(names: list[str], value: Any) -> None:
            if value is None:
                return
            for name in names:
                widget = self._window.findChild(QSpinBox, name)
                if widget is not None:
                    widget.setValue(int(value))

        _set(["spinRepeats"], repeats)
        _set(["spinDelayPreFirst", "spinPreFirst"], delays.get("pre_first"))
        _set(["spinDelayBetweenReps", "spinBetweenReps"], delays.get("between_reps"))
        _set(["spinDelayBeforeHints", "spinBeforeHints"], delays.get("before_hints"))
        _set(["spinDelayBeforeExtras", "spinBeforeExtras"], delays.get("before_extras"))
        _set(["spinDelayAutoAdvance", "spinAutoAdvance"], delays.get("auto_advance"))
