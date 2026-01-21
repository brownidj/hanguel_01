"""Label/widget construction helpers.

Small widget factories used by the UI composition layer.

Keep these helpers purely UI-related: they may create widgets/layouts but should
not read/write settings, start timers, or perform application orchestration.
"""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QSizePolicy,
)


def _mk_title_label(text: str, *, point_size: int = 14, bold: bool = True) -> QLabel:
    """Create a standard title label."""
    lbl = QLabel(text)
    f = QFont()
    f.setPointSize(int(point_size))
    f.setBold(bool(bold))
    lbl.setFont(f)
    lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
    lbl.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
    return lbl


def _make_labeled_column(title: str, body: QWidget, parent: QWidget | None = None) -> QWidget:
    """Create a simple titled column widget.

    Mirrors the legacy calling convention used in `main.py`:
        _make_labeled_column(key: str, widget: QWidget, parent: QWidget) -> QWidget
    """
    outer = QWidget(parent)
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(6)
    layout.addWidget(_mk_title_label(title, point_size=14, bold=True))
    layout.addWidget(body)
    return outer



def _make_labeled_column_custom(
    title: str | QWidget,
    tip_or_body: str | QWidget,
    body: QWidget | None = None,
    parent: QWidget | None = None,
    *,
    title_point_size: int = 14,
    bold: bool = True,
    spacing: int = 6,
    margins: tuple[int, int, int, int] = (0, 0, 0, 0),
) -> QWidget:
    """Wrap a widget with a custom title and return a single container widget.

    Supports two calling conventions:

    1) New style:
        _make_labeled_column_custom(title, body, *, ...)

    2) Legacy style used by `main.py`:
        _make_labeled_column_custom(title, tip, body, parent)

    Where `tip` is a tooltip string associated with the title.

    Args:
        title: Either a string title (rendered via `_mk_title_label`) or a fully
            constructed QWidget (e.g., a QLabel with rich formatting).
        tip_or_body: Either the tooltip string (legacy style) or the body widget (new style).
        body: The main widget to place under the title (legacy style only).
        parent: Optional parent for the returned container (legacy style only).
        title_point_size: Used only when `title` is a string.
        bold: Used only when `title` is a string.
        spacing: Vertical spacing between title and body.
        margins: Contents margins for the outer container.

    Returns:
        A QWidget containing the title widget above the body.
    """

    # --- Resolve calling convention ---
    tooltip: str | None
    body_widget: QWidget
    parent_widget: QWidget | None

    if body is None:
        # New style: (title, body)
        tooltip = None
        body_widget = tip_or_body if isinstance(tip_or_body, QWidget) else QLabel(str(tip_or_body))
        parent_widget = None
    else:
        # Legacy style: (title, tip, body, parent)
        tooltip = str(tip_or_body)
        body_widget = body
        parent_widget = parent

    outer = QWidget(parent_widget)
    layout = QVBoxLayout(outer)
    layout.setContentsMargins(int(margins[0]), int(margins[1]), int(margins[2]), int(margins[3]))
    layout.setSpacing(int(spacing))

    title_widget: QWidget
    if isinstance(title, str):
        title_widget = _mk_title_label(title, point_size=int(title_point_size), bold=bool(bold))
    else:
        title_widget = title

    if tooltip:
        try:
            title_widget.setToolTip(tooltip)
        except Exception:
            pass
        try:
            outer.setToolTip(tooltip)
        except Exception:
            pass

    layout.addWidget(title_widget)
    layout.addWidget(body_widget)
    return outer
