from __future__ import annotations

from typing import Callable, Optional, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QFrame, QLayout, QStackedWidget, QWidget

from app.controllers.block_manager import BlockManager
from app.controllers.template_navigator import TemplateNavigator
from app.ui.utils.qt_find import require_child
from app.ui.widgets.jamo_block import JamoBlock


class JamoBlockController:
    """Builds and wires the Jamo block area."""

    def __init__(
        self,
        *,
        window: QWidget,
        get_current_pair: Optional[Callable[[], tuple[str, str]]] = None,
    ) -> None:
        self._window = window
        self._get_current_pair = get_current_pair
        self._current_pair: tuple[str, str] | None = None

        self.jamo_block: JamoBlock | None = None
        self.stacked: QStackedWidget | None = None
        self.template_nav: TemplateNavigator | None = None
        self.block_manager: BlockManager | None = None
        self.syllable_label: QLabel | None = None

    def wire(self, *, initial_consonant: str, initial_vowel: str) -> None:
        jamo_block = JamoBlock()

        frame = require_child(self._window, QFrame, "frameJamoBorder")
        layout = frame.layout()
        if layout is None:
            raise RuntimeError("frameJamoBorder has no layout")

        cast(QLayout, layout).addWidget(jamo_block)

        self.jamo_block = jamo_block
        setattr(self._window, "_jamo_block", jamo_block)

        stacked = require_child(jamo_block, QStackedWidget, "stackedTemplates")
        self.stacked = stacked
        self.template_nav = TemplateNavigator(stacked)

        self.block_manager = BlockManager()
        setattr(self._window, "_block_manager", self.block_manager)

        syll_label = self._window.findChild(QLabel, "labelSyllableRight")
        self.syllable_label = syll_label
        if syll_label is not None:
            syll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            syll_label.setText("")

        self._current_pair = (initial_consonant, initial_vowel)
        self.block_manager.show_pair(
            stacked=stacked,
            consonant=initial_consonant,
            vowel=initial_vowel,
            syll_label=syll_label,
            type_label=None,
        )

    def go_next_template(self) -> None:
        """Cycle the template page (block type) and re-render on that page."""
        if self.stacked is None or self.block_manager is None:
            return
        count = int(self.stacked.count())
        if count <= 1:
            return
        new_index = (int(self.stacked.currentIndex()) + 1) % count
        self.stacked.setCurrentIndex(new_index)
        consonant, vowel = self._current_pair_for_render()
        block_type = self.block_manager.block_type_for_index(new_index)
        self.block_manager.show_pair_on_type(
            stacked=self.stacked,
            consonant=consonant,
            vowel=vowel,
            block_type=block_type,
            syll_label=self.syllable_label,
            type_label=None,
        )

    def go_prev_template(self) -> None:
        """Cycle the template page (block type) and re-render on that page."""
        if self.stacked is None or self.block_manager is None:
            return
        count = int(self.stacked.count())
        if count <= 1:
            return
        new_index = (int(self.stacked.currentIndex()) - 1) % count
        self.stacked.setCurrentIndex(new_index)
        consonant, vowel = self._current_pair_for_render()
        block_type = self.block_manager.block_type_for_index(new_index)
        self.block_manager.show_pair_on_type(
            stacked=self.stacked,
            consonant=consonant,
            vowel=vowel,
            block_type=block_type,
            syll_label=self.syllable_label,
            type_label=None,
        )

    def _current_pair_for_render(self) -> tuple[str, str]:
        if self._get_current_pair is not None:
            try:
                pair = self._get_current_pair()
                if isinstance(pair, tuple) and len(pair) == 2:
                    self._current_pair = pair
                    return pair
            except Exception:
                pass
        if self._current_pair is not None:
            return self._current_pair
        return ("ㄱ", "ㅏ")
