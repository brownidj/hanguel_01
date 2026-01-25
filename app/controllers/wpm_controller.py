from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QRadioButton, QPushButton, QWidget

from app.services.settings_store import SettingsStore
from app.controllers.pronunciation_controller import PronunciationController


class WpmController:
    """Owns WPM radios + slow-mode toggle behavior."""

    def __init__(
        self,
        *,
        window: QWidget,
        pronouncer: Optional[PronunciationController],
        settings_store: Optional[SettingsStore],
    ) -> None:
        self._window = window
        self._pronouncer = pronouncer
        self._settings_store = settings_store

        self._slow_mode_enabled: bool = False
        self._previous_wpm: int | None = None
        self._current_wpm: int = 120

    def set_pronouncer(self, pronouncer: Optional[PronunciationController]) -> None:
        self._pronouncer = pronouncer

    def wire_wpm_controls(self) -> None:
        if self._settings_store is None:
            return
        radio_40 = self._window.findChild(QRadioButton, "radioWpm40")
        radio_80 = self._window.findChild(QRadioButton, "radioWpm80")
        radio_120 = self._window.findChild(QRadioButton, "radioWpm120")
        radio_160 = self._window.findChild(QRadioButton, "radioWpm160")

        radios = {
            40: radio_40,
            80: radio_80,
            120: radio_120,
            160: radio_160,
        }

        def _apply_wpm(val: int, *, persist: bool = True) -> None:
            self._apply_wpm_value(int(val), persist=persist)

        def _hook(rb: QRadioButton | None, value: int) -> None:
            if rb is None:
                return
            try:
                rb.toggled.disconnect()
            except Exception:
                pass
            rb.toggled.connect(lambda checked: _apply_wpm(value) if checked else None)

        for val, rb in radios.items():
            _hook(rb, val)

        saved = self._settings_store.get_wpm()
        if saved in radios and radios[saved] is not None:
            _apply_wpm(saved, persist=False)
        else:
            _apply_wpm(120, persist=False)

    def init_slow_chip(self) -> None:
        btn = self._window.findChild(QPushButton, "chipSlow")
        if btn is None:
            return
        try:
            btn.setCheckable(True)
            btn.setFlat(False)
        except Exception:
            pass
        self._set_slow_chip_style(False)

    def on_slow_clicked(self) -> None:
        self._slow_mode_enabled = not self._slow_mode_enabled
        self._set_slow_chip_style(self._slow_mode_enabled)
        if self._slow_mode_enabled:
            self._previous_wpm = self.current_wpm_value()
            self._apply_wpm_value(40)
        else:
            restore = self._previous_wpm or self.current_wpm_value()
            self._apply_wpm_value(int(restore))

    def current_wpm_value(self) -> int:
        if self._settings_store is not None:
            try:
                return int(self._settings_store.get_wpm())
            except Exception:
                pass
        return int(self._current_wpm)

    def _apply_wpm_value(self, value: int, *, persist: bool = True) -> None:
        val = max(40, min(160, int(value)))
        self._current_wpm = val
        if self._pronouncer is not None:
            try:
                self._pronouncer.tts.set_rate_wpm(int(val))
            except Exception:
                pass
        if persist and self._settings_store is not None:
            self._settings_store.set_wpm(int(val))
        radio = self._window.findChild(QRadioButton, "radioWpm{}".format(val))
        if radio is not None:
            try:
                if not radio.isChecked():
                    radio.blockSignals(True)
                    radio.setChecked(True)
                    radio.blockSignals(False)
            except Exception:
                pass

    def _set_slow_chip_style(self, on: bool) -> None:
        btn = self._window.findChild(QPushButton, "chipSlow")
        if btn is None:
            return
        try:
            if on:
                btn.setStyleSheet(
                    "QPushButton {"
                    " background-color: #BDBBBB;"
                    " border: 1px solid #888;"
                    " border-radius: 12px;"
                    " padding: 4px 10px;"
                    "}"
                    "QPushButton:pressed { background-color: #B0B0B0; }"
                )
                btn.setChecked(True)
            else:
                btn.setStyleSheet(
                    "QPushButton {"
                    " background-color: #FAFAFA;"
                    " border: 1px solid #BBBBBB;"
                    " border-radius: 12px;"
                    " padding: 4px 10px;"
                    "}"
                    "QPushButton:hover { background-color: #F0F0F0; }"
                )
                btn.setChecked(False)
            btn.update()
        except Exception:
            pass
