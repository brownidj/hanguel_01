from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer

from app.domain.enums import DelaysConfig


class PlaybackSequenceController(QObject):
    """Non-blocking sequencer for repeats + delays with cancel support."""

    def __init__(
        self,
        *,
        tts_play: Callable[[str, Callable[[], None]], None],
        on_reveal_hints: Optional[Callable[[], None]] = None,
        on_reveal_extras: Optional[Callable[[], None]] = None,
        on_autoadvance: Optional[Callable[[], None]] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._tts_play = tts_play
        self._on_reveal_hints = on_reveal_hints or (lambda: None)
        self._on_reveal_extras = on_reveal_extras or (lambda: None)
        self._on_autoadvance = on_autoadvance or (lambda: None)
        self._gen = 0
        self._running = False
        self._on_finished: Optional[Callable[[], None]] = None

    def is_running(self) -> bool:
        return self._running

    def set_on_finished(self, cb: Optional[Callable[[], None]]) -> None:
        self._on_finished = cb

    def cancel(self) -> None:
        self._gen += 1
        if self._running:
            self._running = False
            cb = self._on_finished
            if cb is not None:
                try:
                    cb()
                except Exception:
                    pass
        else:
            self._running = False

    def start(self, glyph: str, repeat_count: int, delays: DelaysConfig, auto_mode: bool = False) -> None:
        self.cancel()
        token = self._gen
        self._running = True

        def _valid() -> bool:
            return self._running and token == self._gen

        def _finish() -> None:
            if not _valid():
                return
            self._running = False
            cb = self._on_finished
            if cb is not None:
                try:
                    cb()
                except Exception:
                    pass

        def _play_n(n_left: int) -> None:
            if not _valid():
                return

            def _after_one() -> None:
                if not _valid():
                    return
                if n_left > 1:
                    QTimer.singleShot(max(0, int(delays.between_reps_ms)), lambda: _play_n(n_left - 1))
                else:
                    _after_repeats()

            try:
                self._tts_play(glyph, _after_one)
            except Exception:
                QTimer.singleShot(0, _after_one)

        def _after_repeats() -> None:
            if not _valid():
                return

            def _do_hints() -> None:
                if not _valid():
                    return
                try:
                    self._on_reveal_hints()
                finally:
                    _after_hints()

            QTimer.singleShot(max(0, int(delays.before_hints_ms)), _do_hints)

        def _after_hints() -> None:
            if not _valid():
                return

            def _do_extras() -> None:
                if not _valid():
                    return
                try:
                    self._on_reveal_extras()
                finally:
                    _after_extras()

            QTimer.singleShot(max(0, int(delays.before_extras_ms)), _do_extras)

        def _after_extras() -> None:
            if not _valid():
                return
            if auto_mode:
                QTimer.singleShot(
                    max(0, int(delays.auto_advance_ms)),
                    lambda: (self._on_autoadvance(), _finish()),
                )
                return
            _finish()

        if delays.pre_first_ms > 0:
            QTimer.singleShot(int(delays.pre_first_ms), lambda: _play_n(max(1, int(repeat_count))))
        else:
            _play_n(max(1, int(repeat_count)))
