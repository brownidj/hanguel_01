from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtWidgets import QLabel, QStackedWidget

from app.domain.block_types import block_type_for_pair
from app.domain.enums import BlockType
from app.domain.hangul_compose import compose_cv
from app.domain.syllables import select_syllable_for_block
from app.ui.jamo.block_container import BlockContainer

logger = logging.getLogger(__name__)

_DEBUG_BLOCK_MANAGER = False


class BlockManager:
    """Caches one BlockContainer per BlockType and preserves per-type state."""

    def __init__(self) -> None:
        self._containers = {
            BlockType.A_RightBranch: BlockContainer(BlockType.A_RightBranch),
            BlockType.B_TopBranch: BlockContainer(BlockType.B_TopBranch),
            BlockType.C_BottomBranch: BlockContainer(BlockType.C_BottomBranch),
            BlockType.D_Horizontal: BlockContainer(BlockType.D_Horizontal),
        }
        self._order = [
            BlockType.A_RightBranch,
            BlockType.B_TopBranch,
            BlockType.C_BottomBranch,
            BlockType.D_Horizontal,
        ]
        self._current_index = 0  # start on Type A
        self._names = [
            "Type A — Right-branching",
            "Type B — Top-branching",
            "Type C — Bottom-branching",
            "Type D — Horizontal",
        ]

    def current_type(self) -> BlockType:
        return self._order[self._current_index]

    def block_type_for_index(self, index: int) -> BlockType:
        if not self._order:
            return BlockType.A_RightBranch
        return self._order[int(index) % len(self._order)]

    def show_consonant(
        self,
        *,
        stacked: QStackedWidget,
        consonant: str,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        # Use A_RightBranch container for a stable consonant-only view
        container = self._containers[BlockType.A_RightBranch]
        container.consonant_only(stacked, consonant)
        self._current_index = 0
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None:
            syll_label.setText(consonant)

    def attach_current(
        self,
        *,
        stacked: QStackedWidget,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        ctype = self.current_type()
        container = self._containers[ctype]
        container.attach(stacked)
        try:
            _glyph = select_syllable_for_block(ctype)
        except Exception:
            _glyph = "?"
        if _DEBUG_BLOCK_MANAGER:
            logger.info(
                "attach_current -> glyph=%s block=%s",
                _glyph,
                ctype.name,
            )
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None and _glyph:
            syll_label.setText(_glyph)

    def show_pair(
        self,
        *,
        stacked: QStackedWidget,
        consonant: str,
        vowel: str,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        bt = block_type_for_pair(consonant, vowel)
        try:
            self._current_index = self._order.index(bt)
        except ValueError:
            self._current_index = 0
        container = self._containers[bt]
        glyph = compose_cv(consonant, vowel) or ""
        if _DEBUG_BLOCK_MANAGER:
            logger.info(
                "show_pair -> consonant=%s vowel=%s glyph=%s block=%s",
                consonant,
                vowel,
                glyph,
                bt.name,
            )
        container.attach(stacked, consonant=consonant, vowel=vowel, glyph=glyph)
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None and glyph:
            syll_label.setText(glyph)

    def show_pair_on_type(
        self,
        *,
        stacked: QStackedWidget,
        consonant: str,
        vowel: str,
        block_type: BlockType,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        try:
            self._current_index = self._order.index(block_type)
        except ValueError:
            self._current_index = 0
        container = self._containers[block_type]
        glyph = compose_cv(consonant, vowel) or ""
        container.attach(stacked, consonant=consonant, vowel=vowel, glyph=glyph)
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None and glyph:
            syll_label.setText(glyph)

    def next(
        self,
        *,
        stacked: QStackedWidget,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        self._current_index = (self._current_index + 1) % len(self._order)
        self.attach_current(stacked=stacked, type_label=type_label, syll_label=syll_label)

    def prev(
        self,
        *,
        stacked: QStackedWidget,
        type_label: Optional[QLabel] = None,
        syll_label: Optional[QLabel] = None,
    ) -> None:
        self._current_index = (self._current_index - 1) % len(self._order)
        self.attach_current(stacked=stacked, type_label=type_label, syll_label=syll_label)
