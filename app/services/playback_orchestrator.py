

"""Playback orchestration for Hangul_01.

This module centralises the "play N times with delays" behaviour so UI code can
stay thin and tests can exercise the logic without needing to run the full app.

Design goals:
- No hard dependency on a specific UI layout.
- Orchestrate *when* to pronounce and when to enable/disable controls.
- Be safe under tests (qtbot) and when called repeatedly.

The orchestrator is intentionally callback-driven:
- It does not know about concrete widgets.
- UI layer provides:
  - `pronounce_fn(text)` to speak/pronounce the current glyph.
  - `lock_controls_fn()` / `unlock_controls_fn()` to toggle UI inputs.
  - `on_cycle_start(i, n)` / `on_cycle_end(i, n)` optional hooks.

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from PyQt6.QtCore import QObject, QTimer


PronounceFn = Callable[[str], None]
VoidFn = Callable[[], None]
CycleHook = Callable[[int, int], None]


# --- Backward-compatible helper for UI code ---
def set_controls_for_repeats_locked(*args, **kwargs) -> None:
    """Backward-compatible helper used by older UI code.

    Purpose:
        Toggle UI controls only when repeats > 1.

    Supported call patterns (best-effort):
        - set_controls_for_repeats_locked(locked: bool, repeats: int, lock_fn: Callable, unlock_fn: Callable)
        - set_controls_for_repeats_locked(repeats: int, locked: bool, lock_fn: Callable, unlock_fn: Callable)
        - set_controls_for_repeats_locked(locked=..., repeats=..., lock_controls_fn=..., unlock_controls_fn=...)

    If repeats <= 1, this is a no-op except that an explicit unlock request will
    attempt to call the unlock callback.
    """

    # --- Extract kwargs first (preferred) ---
    locked_kw = kwargs.get("locked", None)
    repeats_kw = kwargs.get("repeats", None)
    lock_fn_kw = kwargs.get("lock_controls_fn", None) or kwargs.get("lock_fn", None)
    unlock_fn_kw = kwargs.get("unlock_controls_fn", None) or kwargs.get("unlock_fn", None)

    locked: Optional[bool] = bool(locked_kw) if isinstance(locked_kw, bool) else None
    repeats: Optional[int] = int(repeats_kw) if isinstance(repeats_kw, int) else None

    lock_fn: Optional[VoidFn] = lock_fn_kw if callable(lock_fn_kw) else None
    unlock_fn: Optional[VoidFn] = unlock_fn_kw if callable(unlock_fn_kw) else None

    # --- Best-effort positional parsing ---
    pos = list(args)

    # Find the first bool and first int among args (order-insensitive)
    if locked is None:
        for v in pos:
            if isinstance(v, bool):
                locked = bool(v)
                break

    if repeats is None:
        for v in pos:
            if isinstance(v, int) and not isinstance(v, bool):
                repeats = int(v)
                break

    # Collect callables from args (ignore non-callables)
    callables = [v for v in pos if callable(v)]
    if lock_fn is None and len(callables) >= 1:
        lock_fn = callables[0]
    if unlock_fn is None and len(callables) >= 2:
        unlock_fn = callables[1]

    # Sensible defaults
    if repeats is None:
        repeats = 1
    if locked is None:
        locked = True

    # Only lock controls for repeats > 1.
    if int(repeats) > 1:
        if bool(locked):
            try:
                if lock_fn is not None:
                    lock_fn()
            except Exception:
                pass
        else:
            try:
                if unlock_fn is not None:
                    unlock_fn()
            except Exception:
                pass
    else:
        # For repeats <= 1 we normally do nothing, but an explicit unlock request
        # should be honoured.
        if not bool(locked):
            try:
                if unlock_fn is not None:
                    unlock_fn()
            except Exception:
                pass


@dataclass(frozen=True)
class PlaybackConfig:
    """Configuration for a playback cycle."""

    repeats: int = 1
    info_delay_ms: int = 0
    writing_delay_ms: int = 0

    def normalised(self) -> "PlaybackConfig":
        r = int(self.repeats)
        if r < 1:
            r = 1

        info = int(self.info_delay_ms)
        if info < 0:
            info = 0

        writing = int(self.writing_delay_ms)
        if writing < 0:
            writing = 0

        return PlaybackConfig(repeats=r, info_delay_ms=info, writing_delay_ms=writing)


class PlaybackOrchestrator(QObject):
    """Orchestrates timed repeated pronunciations of a glyph.

    Typical flow:
        orchestrator.update_config(repeats, info_delay, writing_delay)
        orchestrator.start(glyph)

    - If repeats <= 1, the orchestrator does *not* lock controls.
    - If repeats > 1, it locks controls on start and unlocks after the final
      cycle completes (or if stop() is called).

    The orchestrator is safe to re-start while already running: it will stop the
    current schedule first.
    """

    def __init__(
        self,
        pronounce_fn: PronounceFn,
        *,
        lock_controls_fn: Optional[VoidFn] = None,
        unlock_controls_fn: Optional[VoidFn] = None,
        on_cycle_start: Optional[CycleHook] = None,
        on_cycle_end: Optional[CycleHook] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)

        if not callable(pronounce_fn):
            raise TypeError("pronounce_fn must be callable")

        self._pronounce_fn: PronounceFn = pronounce_fn
        self._lock_controls_fn: Optional[VoidFn] = lock_controls_fn
        self._unlock_controls_fn: Optional[VoidFn] = unlock_controls_fn
        self._on_cycle_start: Optional[CycleHook] = on_cycle_start
        self._on_cycle_end: Optional[CycleHook] = on_cycle_end

        self._config: PlaybackConfig = PlaybackConfig()
        self._glyph: str = ""
        self._running: bool = False
        self._cycle_index: int = 0

        self._timer: QTimer = QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._advance)  # type: ignore

    # ----------------------------
    # Public API
    # ----------------------------

    def update_config(self, repeats: int, info_delay_ms: int, writing_delay_ms: int) -> None:
        """Update playback configuration (values are clamped to safe ranges)."""
        self._config = PlaybackConfig(
            repeats=repeats,
            info_delay_ms=info_delay_ms,
            writing_delay_ms=writing_delay_ms,
        ).normalised()

    def config(self) -> PlaybackConfig:
        return self._config

    def is_running(self) -> bool:
        return bool(self._running)

    def start(self, glyph: str) -> None:
        """Start playback for a glyph using the current config."""
        if glyph is None:
            glyph = ""
        self.stop()

        self._glyph = str(glyph)
        self._cycle_index = 0
        self._running = True

        # Lock controls only for multi-repeat playback.
        if self._config.repeats > 1:
            self._safe_call(self._lock_controls_fn)

        # Kick off immediately (cycle 1). Any info delay is applied *after*
        # the pronunciation (this matches typical UX: speak then show info).
        self._advance()

    def stop(self) -> None:
        """Stop any scheduled playback and unlock controls if needed."""
        if self._timer.isActive():
            try:
                self._timer.stop()
            except (RuntimeError, ValueError):
                pass

        was_running = self._running
        was_repeating = self._config.repeats > 1

        self._running = False
        self._glyph = ""
        self._cycle_index = 0

        if was_running and was_repeating:
            self._safe_call(self._unlock_controls_fn)

    # ----------------------------
    # Internal scheduling
    # ----------------------------

    def _advance(self) -> None:
        if not self._running:
            return

        n = int(self._config.repeats)
        if n < 1:
            n = 1

        i = int(self._cycle_index)
        if i >= n:
            # Done.
            self._running = False
            if n > 1:
                self._safe_call(self._unlock_controls_fn)
            return

        # Cycle start hook (1-based index for readability)
        self._safe_cycle_hook(self._on_cycle_start, i + 1, n)

        # Pronounce
        try:
            self._pronounce_fn(self._glyph)
        except (RuntimeError, ValueError, TypeError):
            # Do not crash the UI/test runner; stop cleanly.
            self.stop()
            return

        # Cycle end hook
        self._safe_cycle_hook(self._on_cycle_end, i + 1, n)

        self._cycle_index = i + 1

        # Schedule next tick if there are more cycles.
        if self._cycle_index < n:
            delay = self._next_delay_ms()
            try:
                self._timer.start(int(delay))
            except (RuntimeError, ValueError, TypeError, OverflowError):
                # If timers fail (rare in tests), just stop cleanly.
                self.stop()

    def _next_delay_ms(self) -> int:
        """Compute the delay before the next cycle.

        We treat info_delay as the pause after pronunciation for showing info.
        writing_delay is an additional pause to allow user tracing/writing.
        """
        info = int(self._config.info_delay_ms)
        writing = int(self._config.writing_delay_ms)

        if info < 0:
            info = 0
        if writing < 0:
            writing = 0

        return info + writing

    @staticmethod
    def _safe_call(fn: Optional[VoidFn]) -> None:
        if fn is None:
            return
        try:
            fn()
        except Exception:
            pass

    @staticmethod
    def _safe_cycle_hook(fn: Optional[CycleHook], i: int, n: int) -> None:
        if fn is None:
            return
        try:
            fn(int(i), int(n))
        except Exception:
            pass


__all__ = [
    "PlaybackConfig",
    "PlaybackOrchestrator",
    "set_controls_for_repeats_locked",
]