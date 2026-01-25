from __future__ import annotations

from PyQt6.QtWidgets import QHBoxLayout, QWidget


class LayoutStretchController:
    """Apply stretch factors to a named QHBoxLayout."""

    def __init__(self, *, window: QWidget, layout_name: str, stretches: tuple[int, int]) -> None:
        self._window = window
        self._layout_name = layout_name
        self._stretches = stretches

    def wire(self) -> None:
        layout = self._window.findChild(QHBoxLayout, self._layout_name)
        if layout is None:
            return
        if layout.count() < len(self._stretches):
            return
        for idx, stretch in enumerate(self._stretches):
            try:
                layout.setStretch(idx, int(stretch))
            except Exception:
                pass
