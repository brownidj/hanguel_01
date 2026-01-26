from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from typing import Optional, Any

from PyQt6 import uic
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QLabel, QFrame, QStackedWidget

from app.domain.enums import ConsonantPosition
from app.ui.fit_text import AutoFitLabel


class SegmentView(QWidget):
    """A lightweight container widget representing one Hangul block segment.

    The UI uses three segments (Top/Middle/Bottom). We persist the role in two
    ways to make discovery robust:

    1) as an attribute (returned by role()), and
    2) as a dynamic Qt property 'segmentRole' with string values
       {"Top", "Middle", "Bottom"} when possible.

    This enables utilities such as `layout._enforce_equal_segment_heights(...)`
    and renderers to discover segment widgets without relying on object names.

    Architectural note:
        We deliberately do not model segments as a separate BlockSegment class.
        In this codebase a “segment” is simply SegmentRole (Top/Middle/Bottom)
        plus the QWidget that holds presenters, discovered via role() and/or
        the dynamic property 'segmentRole'.
    """

    def __init__(self, parent: Optional[QWidget] = None, role: Any = None) -> None:
        super().__init__(parent)
        self._role = role

        # Best-effort: reflect role into a dynamic property for discovery.
        # Accept either enum-like objects (with .name) or strings.
        try:
            role_name = getattr(role, "name", None)
            if isinstance(role_name, str):
                name = role_name
            elif isinstance(role, str):
                name = role
            else:
                name = None

            if name in ("Top", "Middle", "Bottom"):
                self.setProperty("segmentRole", name)
        except (AttributeError, TypeError, ValueError):
            pass

        # Ensure it always has a layout, because main render code expects one.
        if self.layout() is None:
            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def role(self) -> Any:
        """Return the logical segment role (Top/Middle/Bottom)."""
        return self._role


class _QtABCMeta(ABCMeta, type(QWidget)):
    """Combine ABCMeta with Qt's sip wrapper metaclass to allow abstract Qt widgets."""
    pass


class Characters(QWidget, metaclass=_QtABCMeta):
    """Abstract base for glyph presenters (consonant/vowel)."""

    DEFAULT_MIN_PT = 24
    DEFAULT_MAX_PT = 128
    DEFAULT_PADDING = 4

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            grapheme: str = "",
            ipa: Optional[str] = None,
            *,
            min_pt: int = DEFAULT_MIN_PT,
            max_pt: int = DEFAULT_MAX_PT,
            padding: int = DEFAULT_PADDING,
    ) -> None:
        super().__init__(parent)
        self._grapheme = grapheme
        self._ipa = ipa

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sp_self = self.sizePolicy()
        sp_self.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp_self.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sp_self)

        self._glyph = AutoFitLabel(grapheme, self, min_pt=min_pt, max_pt=max_pt, padding=padding)
        try:
            # Ensure glyphs remain visible even if parent palettes/styles are muted.
            self._glyph.setStyleSheet("color: #000000; background: transparent;")
            self._glyph.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception:
            pass
        layout.addWidget(self._glyph, 1)

    @abstractmethod
    def kind(self) -> str:
        raise NotImplementedError

    def glyph_label(self) -> QLabel:
        return self._glyph

    def set_grapheme(self, g: str) -> None:
        self._grapheme = g
        self._glyph.setText(g)

    def set_ipa(self, ipa: Optional[str]) -> None:
        self._ipa = ipa


class ConsonantView(Characters):
    def __init__(
            self,
            parent: Optional[QWidget] = None,
            grapheme: str = "",
            position: Optional[ConsonantPosition] = None,
            ipa: Optional[str] = None,
    ):
        super().__init__(
            parent,
            grapheme=grapheme,
            ipa=ipa,
            min_pt=self.DEFAULT_MIN_PT,
            max_pt=self.DEFAULT_MAX_PT,
            padding=self.DEFAULT_PADDING,
        )
        self._position = position

    def set_position(self, p: ConsonantPosition) -> None:
        self._position = p

    def kind(self) -> str:
        return "consonant"


class VowelView(Characters):
    def __init__(self, parent: Optional[QWidget] = None, grapheme: str = "", ipa: Optional[str] = None):
        super().__init__(
            parent,
            grapheme=grapheme,
            ipa=ipa,
            min_pt=self.DEFAULT_MIN_PT,
            max_pt=self.DEFAULT_MAX_PT,
            padding=self.DEFAULT_PADDING,
        )

    def kind(self) -> str:
        return "vowel"
