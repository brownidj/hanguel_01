

from __future__ import annotations

from typing import Any, Callable, Optional

from PyQt6.QtCore import QTimer


class PronunciationController:
    """UI-friendly pronunciation adapter.

    Why this exists:
      - Preserve the legacy calling convention used by `main.py` and the playback
        orchestrator while keeping TTS details inside `app.services`.
      - Guarantee that `on_complete` is called even when synthesis/playback fails,
        to prevent UI/orchestrator deadlocks.

    Expected capabilities of the injected backend (duck-typed):
      - Optional: `set_rate_wpm(int)` or `set_wpm(int)`
      - One of:
          * `pronounce_syllable(glyph: str, on_complete: Callable[[], None] | None = None)`
          * `pronounce(glyph: str, on_complete: Callable[[], None] | None = None)`
          * `speak(glyph: str, on_complete: Callable[[], None] | None = None)`
          * `play(glyph: str, on_complete: Callable[[], None] | None = None)`

    Notes:
      - This controller is intentionally small and Qt-aware (uses QTimer) so the
        rest of the application can remain callback-driven.
    """

    class _RateProxy:
        """Compatibility shim so call sites can use `controller.tts.set_rate_wpm(...)`."""

        def __init__(self, backend: Any) -> None:
            self._backend = backend

        def set_rate_wpm(self, wpm: int) -> None:
            try:
                if hasattr(self._backend, "set_rate_wpm"):
                    self._backend.set_rate_wpm(int(wpm))
                    return
                if hasattr(self._backend, "set_wpm"):
                    self._backend.set_wpm(int(wpm))
                    return
            except Exception:
                # Never let UI wiring crash due to rate issues
                pass

    def __init__(self, backend: Any) -> None:
        self._backend = backend
        self.tts = self._RateProxy(backend)

    def pronounce_syllable(self, glyph: str, on_complete: Optional[Callable[[], None]] = None) -> None:
        """Pronounce a glyph and *always* invoke `on_complete` (async-safe)."""

        def _safe_complete() -> None:
            if on_complete is None:
                return
            try:
                on_complete()
            except Exception:
                # Never let callback exceptions break the Qt event loop
                pass

        try:
            # Prefer a backend method that already supports a completion callback.
            for name in ("pronounce_syllable", "pronounce", "speak", "play"):
                if hasattr(self._backend, name):
                    fn = getattr(self._backend, name)
                    try:
                        # Try passing the callback; if unsupported, fall back.
                        fn(glyph, on_complete=_safe_complete)
                        return
                    except TypeError:
                        fn(glyph)
                        # Schedule completion on next tick to keep orchestrator flowing.
                        QTimer.singleShot(0, _safe_complete)
                        return

            # If backend has no known method, still complete.
            QTimer.singleShot(0, _safe_complete)
        except Exception:
            # If anything goes wrong, still complete to avoid deadlocks.
            QTimer.singleShot(0, _safe_complete)