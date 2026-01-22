from __future__ import annotations

from typing import Any, cast

from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QStackedWidget, QPushButton, QSpinBox
from PyQt6.QtWidgets import QLayout

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QFrame, QLabel, QStackedWidget, QPushButton, QSpinBox

from app.ui.widgets.segments import JamoBlock


class MainWindowController:
    """Owns UI wiring and coordination for the main window.

    Navigation explicitly changes the template page by calling
    `QStackedWidget.setCurrentIndex(...)`.
    """

    def __init__(self, window: QWidget, *, settings_path: str | None = None):
        self.window = window
        self.settings_path = settings_path

        self.jamo_block: JamoBlock | None = None
        self.block_manager = None

        # Expose handles for tests that try controller attributes first
        self.next_button: QPushButton | None = None
        self.prev_button: QPushButton | None = None

        self._wire_jamo_block()
        self._wire_controls()
        if self.settings_path:
            self._apply_persisted_settings()

    def _wire_jamo_block(self) -> None:
        from main import BlockManager

        jamo_block = JamoBlock()

        frame = self.window.findChild(QFrame, "frameJamoBorder")
        if frame is None:
            raise RuntimeError("frameJamoBorder not found in main window")

        layout = frame.layout()
        if layout is None:
            raise RuntimeError("frameJamoBorder has no layout")

        layout = cast(QLayout, layout)
        layout.addWidget(jamo_block)

        self.jamo_block = jamo_block
        setattr(self.window, "_jamo_block", jamo_block)

        stacked = jamo_block.findChild(QStackedWidget, "stackedTemplates")
        if stacked is None:
            raise RuntimeError("stackedTemplates not found inside JamoBlock")

        self.block_manager = BlockManager()
        setattr(self.window, "_block_manager", self.block_manager)

        syll_label = self.window.findChild(QLabel, "labelSyllableRight")
        if syll_label is not None:
            syll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            syll_label.setText("")

        self.block_manager.show_pair(
            stacked=stacked,
            consonant="ㄱ",
            vowel="ㅏ",
            syll_label=syll_label,
            type_label=None,
        )

    def _wire_controls(self) -> None:
        jamo_block = self.jamo_block
        if jamo_block is None:
            return

        stacked = jamo_block.findChild(QStackedWidget, "stackedTemplates")
        if stacked is None:
            return

        syll_label = self.window.findChild(QLabel, "labelSyllableRight")

        def _find_button(hints: list[str]) -> QPushButton | None:
            for btn in self.window.findChildren(QPushButton):
                obj = (btn.objectName() or "").lower()
                tip = (btn.toolTip() or "").lower()
                if any(h in obj for h in hints) or any(h in tip for h in hints):
                    return btn
            return None

        next_btn = self.window.findChild(QPushButton, "next_btn") or _find_button(["next"])
        prev_btn = self.window.findChild(QPushButton, "prev_btn") or _find_button(["prev"])

        # controller attributes for test discovery
        self.next_button = next_btn
        self.prev_button = prev_btn

        if next_btn is not None:
            next_btn.clicked.connect(lambda: self._go_next(stacked, syll_label))

        if prev_btn is not None:
            prev_btn.clicked.connect(lambda: self._go_prev(stacked, syll_label))

    def _go_next(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        if stacked.count() <= 0:
            return

        new_index = (stacked.currentIndex() + 1) % stacked.count()
        stacked.setCurrentIndex(new_index)

    def _go_prev(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        if stacked.count() <= 0:
            return

        new_index = (stacked.currentIndex() - 1) % stacked.count()
        stacked.setCurrentIndex(new_index)

    def _apply_persisted_settings(self) -> None:
        from app.services.settings_store import SettingsStore

        store = SettingsStore(settings_path=str(self.settings_path))
        data = store.load() or {}

        repeats = data.get("repeats")
        delays = data.get("delays", {}) if isinstance(data.get("delays", {}), dict) else {}

        def _set(names: list[str], value: Any) -> None:
            if value is None:
                return
            for nm in names:
                w = self.window.findChild(QSpinBox, nm)
                if w is not None:
                    w.setValue(int(value))

        _set(["spinRepeats"], repeats)
        _set(["spinDelayPreFirst", "spinPreFirst"], delays.get("pre_first"))
        _set(["spinDelayBetweenReps", "spinBetweenReps"], delays.get("between_reps"))
        _set(["spinDelayBeforeHints", "spinBeforeHints"], delays.get("before_hints"))
        _set(["spinDelayBeforeExtras", "spinBeforeExtras"], delays.get("before_extras"))
        _set(["spinDelayAutoAdvance", "spinAutoAdvance"], delays.get("auto_advance"))