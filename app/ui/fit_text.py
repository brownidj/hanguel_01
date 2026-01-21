from __future__ import annotations

"""Text fitting helpers (UI utility).

This module is UI-layer support code and therefore Qt-dependent, but it is
intentionally *not* application wiring.

It centralises:
- `_fit_label_font_to_label_rect()`
- `_AutoFitHook` event filter
- `AutoFitLabel` convenience widget

These utilities are used to size large glyph labels to fit their container.
"""

from typing import Optional

from PyQt6.QtCore import QObject, QEvent
from PyQt6.QtGui import QFont, QFontMetrics
from PyQt6.QtWidgets import QLabel, QWidget


def _fit_label_font_to_label_rect(
    label: QLabel,
    target: Optional[QWidget] = None,
    *,
    min_pt: int = 8,
    max_pt: int = 600,
    padding_px: int = 6,
) -> None:
    """Resize `label` font so its text fits within `target`.

    Backward compatible with legacy usage where `target` is omitted and the
    label itself is the constraint.
    """
    try:
        text = label.text() or ""
    except Exception:
        return

    text = str(text).strip()
    if not text:
        return

    if target is None:
        target = label

    try:
        rect = target.contentsRect()
        avail_w = max(0, rect.width() - 2 * int(padding_px))
        avail_h = max(0, rect.height() - 2 * int(padding_px))
    except Exception:
        return

    if avail_w <= 0 or avail_h <= 0:
        return

    try:
        base_font = QFont(label.font())
    except Exception:
        base_font = QFont()

    def fits(pt: int) -> bool:
        f = QFont(base_font)
        try:
            f.setPointSize(int(pt))
        except Exception:
            return False

        fm = QFontMetrics(f)
        try:
            w = int(fm.horizontalAdvance(text))
        except Exception:
            try:
                w = int(fm.boundingRect(text).width())
            except Exception:
                return False

        try:
            h = int(fm.height())
        except Exception:
            return False

        return (w <= avail_w) and (h <= avail_h)

    lo = int(min_pt)
    hi = int(max_pt)
    best = lo

    if lo < 1:
        lo = 1
    if hi < lo:
        hi = lo

    while lo <= hi:
        mid = (lo + hi) // 2
        if fits(mid):
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1

    try:
        new_font = QFont(base_font)
        new_font.setPointSize(int(best))
        label.setFont(new_font)
    except Exception:
        return


class _AutoFitHook(QObject):
    """Event filter that resizes a label font to fit a target widget (optional)."""

    def __init__(self, label: QLabel, target: Optional[QWidget] = None) -> None:
        super().__init__()
        self._label: QLabel = label
        self._target: Optional[QWidget] = target

    def eventFilter(self, obj: QObject, event: QEvent) -> bool:  # noqa: N802
        try:
            et = event.type()
        except Exception:
            return False

        if et in (QEvent.Type.Resize, QEvent.Type.Show, QEvent.Type.LayoutRequest):
            _fit_label_font_to_label_rect(self._label, self._target)

        return False


class AutoFitLabel(QLabel):
    """A QLabel that auto-fits its font size into a companion target widget."""

    def __init__(
        self,
        *args,
        target: Optional[QWidget] = None,
        min_pt: int = 8,
        max_pt: int = 600,
        padding_px: int = 6,
        padding: Optional[int] = None,
        **kwargs,
    ) -> None:
        # Backward compatibility: callers may pass padding=... either explicitly
        # or inside kwargs.
        if "padding" in kwargs:
            try:
                padding = int(kwargs.pop("padding"))
            except Exception:
                try:
                    kwargs.pop("padding", None)
                except Exception:
                    pass

        if padding is not None:
            try:
                padding_px = int(padding)
            except Exception:
                pass

        super().__init__(*args, **kwargs)

        self._min_pt = int(min_pt)
        self._max_pt = int(max_pt)
        self._padding_px = int(padding_px)

        self._auto_fit_target: Optional[QWidget] = None
        self._auto_fit_hook: Optional[_AutoFitHook] = None

        if target is not None:
            self.attach_target(target)
        else:
            _fit_label_font_to_label_rect(
                self,
                None,
                min_pt=self._min_pt,
                max_pt=self._max_pt,
                padding_px=self._padding_px,
            )

    def attach_target(self, target: QWidget) -> None:
        self._auto_fit_target = target
        self._auto_fit_hook = _AutoFitHook(self, target)
        try:
            target.installEventFilter(self._auto_fit_hook)
        except Exception:
            pass

        _fit_label_font_to_label_rect(
            self,
            target,
            min_pt=self._min_pt,
            max_pt=self._max_pt,
            padding_px=self._padding_px,
        )

    def setText(self, text: str) -> None:  # noqa: N802
        super().setText(text)
        _fit_label_font_to_label_rect(
            self,
            self._auto_fit_target,
            min_pt=self._min_pt,
            max_pt=self._max_pt,
            padding_px=self._padding_px,
        )
