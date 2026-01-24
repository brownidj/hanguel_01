"""
Functions in this module should not depend on application state.
"""

from __future__ import annotations

from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QLayout,
    QLabel,
    QSizePolicy,
    QVBoxLayout,
)

from app.ui.widgets.segments import Characters


def _deep_clear_container(container: QWidget | QLayout) -> None:
    """Remove all child widgets and layouts from a container."""
    if isinstance(container, QWidget):
        layout = container.layout()
        if layout is None:
            # Placeholder frames/widgets may not have a layout set in Qt Designer.
            # Create a deterministic empty layout so clearing/attach logic can proceed.
            layout = QVBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
    else:
        layout = container

    while layout.count():
        item = layout.takeAt(0)
        if item is None:
            continue
        widget = item.widget()
        if widget is not None:
            widget.deleteLater()
        else:
            child_layout = item.layout()
            if child_layout is not None:
                _deep_clear_container(child_layout)

    if isinstance(container, QWidget):
        container.update()


def _ensure_empty_placeholder(container: QWidget | QLayout) -> QLabel:
    """Ensure the container has a single placeholder QLabel, clearing others."""
    _deep_clear_container(container)

    label = QLabel("(empty)")
    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    if isinstance(container, QWidget):
        layout = container.layout()
        if layout is None:
            layout = QVBoxLayout(container)
        layout.addWidget(label)
    else:
        container.addWidget(label)

    return label


def _enforce_equal_segment_heights(segments: QWidget | list[QWidget]) -> None:
    """Set all segments to have equal minimum height.

    This helper accepts either:
        * a list of segment widgets, or
        * a parent/container QWidget from which segment widgets can be discovered.

    Discovery is intentionally lightweight (no application-state dependencies):
    it looks for child widgets that declare a dynamic property `segmentRole` set
    to one of: "Top", "Middle", "Bottom".
    """

    segs: list[QWidget] = []

    if isinstance(segments, QWidget):
        page = segments

        # Preferred: dynamic property marker.
        for w in page.findChildren(QWidget):
            try:
                prop = w.property("segmentRole")
            except Exception:
                prop = None
            if prop in ("Top", "Middle", "Bottom"):
                segs.append(w)

        # Fallback: common objectName patterns used in legacy UI files.
        if not segs:
            wanted_suffixes = ("segmentTop", "segmentMiddle", "segmentBottom")
            for w in page.findChildren(QWidget):
                try:
                    name = w.objectName() or ""
                except Exception:
                    name = ""
                if any(name.endswith(suf) for suf in wanted_suffixes):
                    segs.append(w)
    else:
        segs = list(segments)

    # Need at least 2 to make "equal heights" meaningful.
    if len(segs) < 2:
        return

    max_height = 0
    for segment in segs:
        segment.adjustSize()
        height = segment.sizeHint().height()
        if height > max_height:
            max_height = height

    if max_height <= 0:
        return

    for segment in segs:
        segment.setMinimumHeight(max_height)


def _extract_title_and_glyph(text: str) -> tuple[str, str]:
    """Split a combined label string into (title, glyph).

    This helper is intentionally tolerant of formatting variations that may exist
    in UI labels (e.g., "Title: 가", "Title\n가", "Title — 가").

    Args:
        text: The full label text.

    Returns:
        (title, glyph) where either element may be an empty string.
    """
    s = (text or "").strip()
    if not s:
        return "", ""

    # Prefer newline separation if present.
    if "\n" in s:
        parts = [p.strip() for p in s.split("\n") if p.strip()]
        if len(parts) >= 2:
            return parts[0], parts[1]
        return parts[0], ""

    # Common separators.
    for sep in (":", "—", "-", "|"):
        if sep in s:
            left, right = s.split(sep, 1)
            return left.strip(), right.strip()

    # Fallback: if the string ends with a single non-space glyph-like token,
    # treat the last token as glyph.
    tokens = s.split()
    if len(tokens) >= 2:
        return " ".join(tokens[:-1]).strip(), tokens[-1].strip()

    return s, ""


def has_glyph_content(seg_w: Optional[QWidget]) -> bool:
    """Return True if the segment contains any real glyph presenter widgets."""
    if seg_w is None:
        return False
    for w in seg_w.findChildren(QWidget):
        if isinstance(w, Characters):
            return True
    return False
