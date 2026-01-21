from __future__ import annotations

"""Icon helpers (UI utility).

This module is Qt-dependent and intentionally contains no application wiring.

It centralises:
- `build_hamburger_icon()`
- `safe_icon_from_path()`

These were previously defined inline in `main.py`.
"""

from pathlib import Path
from functools import lru_cache
from typing import Optional

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QIcon, QPainter, QPen, QPixmap


@lru_cache(maxsize=256)
def _cached_icon_from_path(abs_path: str, mtime_ns: int) -> QIcon:
    """Cached icon loader.

    Args:
        abs_path: Absolute filesystem path (as a string).
        mtime_ns: File modified timestamp (nanoseconds).

    Returns:
        QIcon instance (may be null).
    """
    try:
        return QIcon(abs_path)
    except (TypeError, ValueError, OSError, RuntimeError):
        return QIcon()


def safe_icon_from_path(path: str | Path) -> QIcon:
    """Load an icon from a filesystem path.

    If the path does not exist or loading fails, a *null* QIcon is returned.
    This avoids raising exceptions at call sites and keeps UI code simple.
    """
    try:
        p = Path(path).expanduser()
        if not p.exists():
            return QIcon()

        ap = str(p.resolve())
        try:
            mtime_ns = p.stat().st_mtime_ns
        except (FileNotFoundError, PermissionError, OSError):
            mtime_ns = 0

        return _cached_icon_from_path(ap, int(mtime_ns))
    except (TypeError, ValueError, AttributeError, OSError):
        return QIcon()


@lru_cache(maxsize=128)
def _cached_hamburger_icon(
    size: int,
    line_thickness: int,
    padding: int,
    rgba: tuple[int, int, int, int] | None,
) -> QIcon:
    """Cached hamburger icon generator.

    The cache key is purely value-based, so callers can request icons repeatedly
    without repeatedly allocating pixmaps.
    """
    try:
        px = QPixmap(QSize(int(size), int(size)))
        px.fill(Qt.GlobalColor.transparent)

        painter = QPainter(px)
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            if rgba is None:
                c = QColor(40, 40, 40)
            else:
                c = QColor(rgba[0], rgba[1], rgba[2], rgba[3])
            pen = QPen(c)
            pen.setWidth(int(line_thickness))
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)

            w = int(size)
            pad = int(padding)
            x1 = pad
            x2 = max(pad, w - pad)

            # Three evenly spaced horizontal lines
            y_top = pad + int(line_thickness)
            y_mid = w // 2
            y_bot = w - pad - int(line_thickness)

            painter.drawLine(x1, y_top, x2, y_top)
            painter.drawLine(x1, y_mid, x2, y_mid)
            painter.drawLine(x1, y_bot, x2, y_bot)
        finally:
            painter.end()

        return QIcon(px)
    except (TypeError, ValueError, OSError, RuntimeError):
        return QIcon()


def build_hamburger_icon(
    size: int = 18,
    *,
    line_thickness: int = 2,
    padding: int = 3,
    color: Optional[QColor] = None,
) -> QIcon:
    """Build a simple, resolution-independent "hamburger" menu icon.

    Args:
        size: Square icon size in pixels.
        line_thickness: Thickness of each bar.
        padding: Inner padding from edges.
        color: Optional QColor for the bars. If omitted, uses a dark grey.

    Returns:
        QIcon instance.
    """
    try:
        rgba = None
        if color is not None:
            rgba = (int(color.red()), int(color.green()), int(color.blue()), int(color.alpha()))
        return _cached_hamburger_icon(int(size), int(line_thickness), int(padding), rgba)
    except (TypeError, ValueError, OSError, RuntimeError):
        return QIcon()
