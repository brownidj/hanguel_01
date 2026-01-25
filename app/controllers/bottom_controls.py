from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Callable

from PyQt6.QtWidgets import QPushButton, QWidget

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BottomControls:
    """Discovers and wires the 5 bottom-row icon buttons.

    Responsibilities:
    - locate buttons (currently by emoji text)
    - enforce stable objectNames (including test-required `chipPronounce`)
    - attach callbacks for each action

    This class does NOT implement behaviour; callers inject handlers.
    """

    def wire(
            self,
            window: QWidget,
            *,
            on_auto: Callable[[], None],
            on_slow: Callable[[], None],
            on_prev: Callable[[], None],
            on_play: Callable[[], None],
            on_next: Callable[[], None] | None = None,
    ) -> None:
        mapping: dict[str, str] = {
            "🚀": "chipAuto",
            "🐢": "chipSlow",
            "◀": "chipPrev",
            "🔊": "chipPronounce",
            "▶": "chipNext",
        }

        handlers: dict[str, Callable[[], None]] = {
            "chipAuto": on_auto,
            "chipSlow": on_slow,
            "chipPrev": on_prev,
            "chipPronounce": on_play,
        }
        if on_next is not None:
            handlers["chipNext"] = on_next

        try:
            buttons = list(window.findChildren(QPushButton))
        except (AttributeError, RuntimeError):
            return

        for btn in buttons:
            try:
                text = (btn.text() or "").strip()
            except (AttributeError, RuntimeError):
                continue

            if text not in mapping:
                continue

            desired_name = mapping[text]

            # Preserve a stable identity (useful if UI objectNames change later).
            try:
                btn.setProperty("bottomControlName", desired_name)
            except (AttributeError, RuntimeError):
                pass

            try:
                if (btn.objectName() or "") != desired_name:
                    btn.setObjectName(desired_name)
            except (AttributeError, RuntimeError):
                pass

            handler = handlers.get(desired_name)
            if handler is None:
                continue

            try:
                btn.clicked.connect(lambda _checked=False, h=handler: h())
            except (AttributeError, RuntimeError):
                pass
