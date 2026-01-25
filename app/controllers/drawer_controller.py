from __future__ import annotations

from typing import Optional

from PyQt6.QtWidgets import QFrame


class DrawerController:
    """Owns drawer visibility toggling (no UI discovery)."""

    def __init__(self, drawer: Optional[QFrame]) -> None:
        self._drawer: Optional[QFrame] = None
        self.set_drawer(drawer)

    def set_drawer(self, drawer: Optional[QFrame]) -> None:
        self._drawer = drawer

    def toggle(self) -> None:
        if self._drawer is None:
            return
        try:
            self._drawer.setVisible(not bool(self._drawer.isVisible()))
        except Exception:
            pass

    def hide(self) -> None:
        if self._drawer is None:
            return
        try:
            self._drawer.setVisible(False)
        except Exception:
            pass
