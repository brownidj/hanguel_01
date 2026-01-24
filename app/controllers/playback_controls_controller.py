from __future__ import annotations

from enum import Enum, auto
from typing import Optional, cast

from PyQt6.QtWidgets import QWidget


class PlayChipState(Enum):
    PLAY = auto()
    REPEAT = auto()


current_chip_state = PlayChipState.PLAY

# --- Slow mode globals (module scope) ---
_slow_mode_enabled = False
_previous_wpm: int | None = None


def set_controls_for_repeats_locked(window: QWidget, locked: bool) -> None:
    """Enable/disable main controls during multi-repeat playback.

    Args:
        window: The main window instance.
        locked: If True, disable controls; if False, re-enable.
    """
    try:
        is_enabled = not bool(locked)

        # These objectNames are referenced by tests and by the UI.
        names = [
            "chipPronounce",
            "chipNext",
            "chipPrev",
            "chipSlow",
            "buttonNext",
            "buttonPrev",
            "comboMode",
        ]

        for name in names:
            try:
                w = cast(Optional[QWidget], window.findChild(QWidget, name))
                if w is not None:
                    w.setEnabled(is_enabled)
            except Exception:
                pass

    except Exception:
        # Never allow UI locking to crash tests or runtime.
        pass
