from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtWidgets import QPushButton, QWidget

from app.controllers.playback_controls_controller import PlayChipState, set_controls_for_repeats_locked
from app.controllers.playback_sequence_controller import PlaybackSequenceController
from app.domain.enums import DelaysConfig


class PlaybackUiController:
    """Owns playback + chip UI behavior (listen/auto/prev/next)."""

    def __init__(
        self,
        *,
        window: QWidget,
        tts_play: Callable[[str, Callable[[], None]], None],
        get_glyph: Callable[[], str],
        get_repeats: Callable[[], int],
        get_delays: Callable[[], DelaysConfig],
        on_next: Callable[[], None],
        on_prev: Callable[[], None],
    ) -> None:
        self._window = window
        self._tts_play = tts_play
        self._get_glyph = get_glyph
        self._get_repeats = get_repeats
        self._get_delays = get_delays
        self._on_next = on_next
        self._on_prev = on_prev

        self._playback_seq: Optional[PlaybackSequenceController] = None
        self._chip_state: PlayChipState = PlayChipState.PLAY
        self._auto_mode_enabled: bool = False
        self._chips_armed: bool = False

    def init_chips(self) -> None:
        self._chips_armed = False
        self._auto_mode_enabled = False
        self._chip_state = PlayChipState.PLAY
        self._init_auto_chip()
        self._set_bottom_chips_enabled(False, keep_listen_enabled=True, keep_auto_enabled=False)

    def _ensure_playback_sequence(self) -> None:
        if self._playback_seq is not None:
            return

        def _auto_advance() -> None:
            self._on_next()
            if self._auto_mode_enabled:
                self.start_playback(auto_mode=True)

        self._playback_seq = PlaybackSequenceController(
            tts_play=self._tts_play,
            on_reveal_hints=lambda: None,
            on_reveal_extras=lambda: None,
            on_autoadvance=_auto_advance,
            parent=self._window,
        )
        self._playback_seq.set_on_finished(self._on_playback_finished)

    def start_playback(self, *, auto_mode: bool = False) -> None:
        glyph = self._get_glyph()
        if not glyph:
            return
        self._ensure_playback_sequence()
        if self._playback_seq is None:
            return
        repeats = self._get_repeats()
        self._set_bottom_chips_enabled(False, keep_listen_enabled=False, keep_auto_enabled=True)
        if repeats > 1:
            set_controls_for_repeats_locked(self._window, True)
        self._playback_seq.start(
            glyph=glyph,
            repeat_count=repeats,
            delays=self._get_delays(),
            auto_mode=bool(auto_mode),
        )

    def on_listen_clicked(self) -> None:
        glyph = self._get_glyph()
        if not glyph:
            return
        if not self._chips_armed:
            self._chips_armed = True
        self.start_playback(auto_mode=False)
        if self._chip_state == PlayChipState.PLAY:
            self._chip_state = PlayChipState.REPEAT

    def on_chip_next(self) -> None:
        if self._playback_seq is not None:
            self._playback_seq.cancel()
        self._on_next()
        self.start_playback(auto_mode=False)

    def on_chip_prev(self) -> None:
        if self._playback_seq is not None:
            self._playback_seq.cancel()
        self._on_prev()
        self.start_playback(auto_mode=False)

    def on_auto_clicked(self) -> None:
        self._auto_mode_enabled = not self._auto_mode_enabled
        self._set_auto_chip_style(self._auto_mode_enabled)
        if not self._auto_mode_enabled:
            if self._playback_seq is not None:
                self._playback_seq.cancel()
            set_controls_for_repeats_locked(self._window, False)
            if self._chips_armed:
                self._set_bottom_chips_enabled(True)
            else:
                self._set_bottom_chips_enabled(False, keep_listen_enabled=True, keep_auto_enabled=False)
            return
        if self._chip_state == PlayChipState.PLAY:
            self._chip_state = PlayChipState.REPEAT
        self._set_bottom_chips_enabled(False, keep_listen_enabled=False, keep_auto_enabled=True)
        self.start_playback(auto_mode=True)

    def _set_bottom_chips_enabled(
        self,
        enabled: bool,
        *,
        keep_listen_enabled: bool = True,
        keep_auto_enabled: bool = True,
    ) -> None:
        states = {
            "chipPrev": enabled,
            "chipNext": enabled,
            "chipSlow": enabled,
            "chipPronounce": True if keep_listen_enabled else enabled,
            "chipAuto": True if keep_auto_enabled else enabled,
        }
        for name, state in states.items():
            btn = self._window.findChild(QPushButton, name)
            if btn is None:
                continue
            try:
                btn.setEnabled(bool(state))
            except Exception:
                pass

    def _on_playback_finished(self) -> None:
        set_controls_for_repeats_locked(self._window, False)
        if self._auto_mode_enabled:
            self._set_bottom_chips_enabled(False, keep_listen_enabled=False, keep_auto_enabled=True)
            return
        if self._chips_armed:
            self._set_bottom_chips_enabled(True)
        else:
            self._set_bottom_chips_enabled(False, keep_listen_enabled=True, keep_auto_enabled=False)

    def _init_auto_chip(self) -> None:
        btn = self._window.findChild(QPushButton, "chipAuto")
        if btn is None:
            return
        try:
            btn.setCheckable(True)
            btn.setFlat(False)
        except Exception:
            pass
        self._set_auto_chip_style(False)

    def _set_auto_chip_style(self, on: bool) -> None:
        btn = self._window.findChild(QPushButton, "chipAuto")
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
