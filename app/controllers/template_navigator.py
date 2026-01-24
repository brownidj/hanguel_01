from __future__ import annotations

from dataclasses import dataclass

from PyQt6.QtWidgets import QStackedWidget, QWidget


@dataclass
class TemplateNavigator:
    """
    Owns template-page navigation (next/prev/wrap) for the stacked widget.

    `MainWindowController` should remain responsible for:
      - deciding WHAT to render
      - calling the single authoritative render/update path

    This class only changes the current template page and returns the new index.
    """

    stacked: QStackedWidget

    def _count(self) -> int:
        try:
            return int(self.stacked.count())
        except (AttributeError, RuntimeError, TypeError):
            return 0

    def current_index(self) -> int:
        try:
            return int(self.stacked.currentIndex())
        except (AttributeError, RuntimeError, TypeError):
            return 0

    def set_index(self, index: int) -> int:
        n = self._count()
        if n <= 0:
            return 0

        i = int(index) % n
        self.stacked.setCurrentIndex(i)
        return i

    def next(self) -> int:
        """Advance to next template page (wrap-around). Returns new index."""
        return self.set_index(self.current_index() + 1)

    def prev(self) -> int:
        """Go to previous template page (wrap-around). Returns new index."""
        return self.set_index(self.current_index() - 1)

    def current_page(self) -> QWidget | None:
        try:
            return self.stacked.currentWidget()
        except (AttributeError, RuntimeError, TypeError):
            return None

    def current_page_name(self) -> str:
        page = self.current_page()
        try:
            return page.objectName() if page is not None else ""
        except (AttributeError, RuntimeError, TypeError):
            return ""