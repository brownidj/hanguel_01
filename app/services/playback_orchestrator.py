"""hangul_01.playback_orchestrator

Phase 4D — Test debt (formal deferrals)
--------------------------------------
This module is a UI-agnostic boundary responsible for playback timing/sequencing.

The test suite currently contains *intentional skips* that MUST remain visible and
owned. Nothing in this file should silently depend on skipped behaviour.

Deferred items (with explicit ownership and re-enable criteria):

1) Glyph discovery tests (HANGUL_TEST_MODE exposure)
   - Status: Deferred (intentional skip)
   - Owner: Hangul_01 maintainer
   - Rationale: Production rendering may be custom-painted; widget discovery is not
     guaranteed unless a dedicated test exposure mode is enabled.
   - Re-enable / completion criteria:
     a) Provide a deterministic, widget-discoverable representation of glyphs when
        `HANGUL_TEST_MODE=1` (or equivalent flag) is set.
     b) Document the exact exposure contract (objectNames, hierarchy, lifetime).
     c) Update tests to assert against that contract (no heuristics).

2) Cached TTS ensure/get-or-build tests
   - Status: Deferred (intentional skip)
   - Owner: Hangul_01 maintainer
   - Rationale: The application does not yet expose a stable public API for ensuring
     cached WAV assets exist (e.g., `ensure_cached_wav(...)` / `get_or_build(...)`).
   - Re-enable / completion criteria:
     a) Introduce a public, importable cache boundary with a minimal contract:
        - deterministic filename mapping
        - existence check
        - build/synthesis hook
        - error signalling
     b) Cover cache hit/miss paths with unit tests.

If these deferrals are no longer desired, remove the skips by implementing the
criteria above and updating the associated tests.
"""
# TODO (Phase 4D follow-up)
# --------------------------------------
# The following test deferrals are INTENTIONAL but MUST be revisited.
# Do not allow these skips to become permanent.
#
# 1) Glyph discovery tests (HANGUL_TEST_MODE)
#    - Implement deterministic glyph/widget exposure for tests.
#    - Remove skip once exposure contract is defined and documented.
#
# 2) Cached TTS ensure/get-or-build tests
#    - Introduce a public cache boundary (ensure/get_or_build).
#    - Remove skip once cache hit/miss behaviour is fully testable.
#
# Owner: Hangul_01 maintainer
# Tracking: Phase 4D
from __future__ import annotations

from typing import Optional

from dataclasses import dataclass


# Public API: Delays
@dataclass(frozen=True)
class Delays:
    pre_first: int = 0
    between_reps: int = 0

from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class PlaybackOrchestrator(QObject):
    """
    Centralised controller for playback timing and sequencing.

    Responsibilities:
    - Own all QTimers
    - Enforce repeat counts and delays
    - Expose explicit lifecycle transitions

    This class deliberately knows NOTHING about widgets.

    Note: Some higher-level integration tests are intentionally deferred (Phase 4D).
    See the module docstring for explicit ownership and completion criteria.

    API Stability: Methods marked "Public API" are considered stable; all others are internal and may change without notice.
    """

    # ---- Public API (Stable) ----
    """
    Stable interface:
      - start(...)
      - stop()
      - is_playing()
      - lifecycle signals: started, stopped, cycle_started, cycle_finished
    """

    # ---- lifecycle signals ----
    started = pyqtSignal()
    stopped = pyqtSignal()
    cycle_started = pyqtSignal(int)
    cycle_finished = pyqtSignal(int)

    def __init__(self, *, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)

        self._playing: bool = False
        self._is_running: bool = False
        self._current_cycle: int = 0
        self._repeats: int = 1
        self._delay_pre_first: int = 0
        self._delay_between_reps: int = 0
        self._pending_finish: bool = False

        # single internal timer
        self._timer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timeout)

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def play(self) -> None:
        raise RuntimeError(
            "play() is deprecated; use start(repeat_count=..., delay_pre_first=..., delay_between_reps=...)"
        )

    # Public API
    def start(
        self,
        *,
        glyph: str | None = None,
        repeat_count: int,
        delays: Delays = Delays(),
        auto_mode: bool = False,
    ) -> None:
        # glyph and auto_mode are accepted for API compatibility
        # PlaybackOrchestrator is UI-agnostic and does not act on them yet
        if self._playing:
            raise RuntimeError("Playback already in progress")

        if not isinstance(repeat_count, int) or repeat_count < 1:
            raise ValueError("repeat_count must be an integer >= 1")

        for name, value in {
            "delays.pre_first": delays.pre_first,
            "delays.between_reps": delays.between_reps,
        }.items():
            if not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be an integer >= 0")

        self._repeats = repeat_count
        self._delay_pre_first = delays.pre_first
        self._delay_between_reps = delays.between_reps

        self._playing = True
        self._is_running = True
        self._current_cycle = 1
        self._pending_finish = False
        self.started.emit()

        # If there is no pre-first delay, emit the first cycle_started synchronously so
        # test waitUntil callbacks never see an empty (non-bool) return.
        if self._delay_pre_first == 0:
            self.cycle_started.emit(self._current_cycle)
            self._pending_finish = True
            self._timer.start(0)
            return

        # Otherwise begin after the configured pre-first delay.
        self._timer.start(self._delay_pre_first)

    # Public API
    def stop(self) -> None:
        if not self._playing:
            return

        self._timer.stop()
        self._pending_finish = False
        self._playing = False
        self._is_running = False
        self._current_cycle = 1
        self.stopped.emit()

    def next(self) -> None:
        """
        Interrupt current playback and advance externally.
        """
        self.stop()

    def prev(self) -> None:
        """
        Interrupt current playback and move backward externally.
        """
        self.stop()

    # Public API
    def is_playing(self) -> bool:
        return self._playing

    # ------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Internal flow
    # ------------------------------------------------------------

    # Internal API (not for external use)
    def _begin_cycle(self) -> None:
        if not self._playing:
            return

        self.cycle_started.emit(self._current_cycle)
        self._pending_finish = True
        # Yield to the Qt event loop so observers/tests can see intermediate state.
        self._timer.start(0)

    # Internal API (not for external use)
    def _finish_cycle(self) -> None:
        if not self._playing:
            return

        self.cycle_finished.emit(self._current_cycle)
        self._current_cycle += 1

        if self._current_cycle > self._repeats:
            self.stop()
            return

        self._timer.start(self._delay_between_reps)

    # Internal API (not for external use)
    def _on_timeout(self) -> None:
        if not self._playing:
            return

        if self._pending_finish:
            self._pending_finish = False
            self._finish_cycle()
            return

        self._begin_cycle()