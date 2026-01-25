from __future__ import annotations

from typing import Callable

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.controllers.study_item_repository import StudyItemRepository
from app.ui.utils.qt_find import find_child


class ConsonantSidebarController:
    """Show a faint consonant-major sidebar with the current consonant highlighted."""

    _VISIBLE_COUNT = 9

    def __init__(
        self,
        *,
        window: QWidget,
        get_mode_text: Callable[[], str],
        get_current_pair: Callable[[], tuple[str, str]],
        repo: StudyItemRepository | None = None,
        container_name: str = "syllableConsonantSidebar",
    ) -> None:
        self._window = window
        self._get_mode_text = get_mode_text
        self._get_current_pair = get_current_pair
        self._repo = repo or StudyItemRepository()
        self._container_name = container_name
        self._container: QWidget | None = None
        self._layout: QVBoxLayout | None = None
        self._labels: list[QLabel] = []
        self._consonants: list[str] = []

    def wire(self) -> None:
        self._container = find_child(self._window, QWidget, self._container_name)
        if self._container is None:
            return
        layout = self._container.layout()
        if not isinstance(layout, QVBoxLayout):
            return
        self._layout = layout
        self._build_labels()
        self.update()

    def update(self) -> None:
        if self._container is None:
            return
        mode = (self._get_mode_text() or "").strip().lower()
        if mode != "syllables":
            self._container.setVisible(False)
            return
        self._container.setVisible(True)
        if not self._consonants:
            return
        consonant, _ = self._get_current_pair()
        try:
            current_index = self._consonants.index(consonant)
        except ValueError:
            current_index = 0
        total = len(self._consonants)
        window = min(self._VISIBLE_COUNT, total)
        start = max(0, min(current_index - window // 2, total - window))
        visible = self._consonants[start : start + window]

        for label in self._labels:
            label.setText("")
            label.setStyleSheet("color: #bbbbbb;")

        for idx, glyph in enumerate(visible):
            label = self._labels[idx]
            label.setText(glyph)
            if glyph == consonant:
                label.setStyleSheet("color: #222222; font-weight: 600;")

    def _build_labels(self) -> None:
        if self._layout is None:
            return
        # Clear existing items if re-wired.
        while self._layout.count():
            item = self._layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._labels.clear()

        self._consonants = [c for c, _ in self._repo.consonant_pairs()]
        count = min(self._VISIBLE_COUNT, max(0, len(self._consonants)))
        for _ in range(count):
            label = QLabel("", self._container)
            label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("color: #bbbbbb;")
            self._layout.addWidget(label)
            self._labels.append(label)
