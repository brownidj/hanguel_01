import sys
from enum import Enum, auto
from typing import Optional, cast

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QLabel,
)

from app.domain.block_types import block_type_for_pair
from app.domain.enums import (
    BlockType,
    SegmentRole,
)
from app.domain.hangul_compose import compose_cv
from app.domain.jamo_data import (
    get_consonant_order,
    get_vowel_order_basic10,
    get_vowel_order_advanced
)
from app.domain.syllables import select_syllable_for_block
from app.ui.jamo.block_container import BlockContainer
from app.ui.main_window import create_main_window
# -------------------------------------------------
#      TEST WINDOW FACTORY FOR PYTEST
# -------------------------------------------------


def create_main_window_for_tests(settings_path: str | None = None):
    """
    Create the main window without starting the Qt event loop.

    This factory exists solely for pytest scaffolds that need a fully
    constructed window without calling app.exec().

    Returns:
        (window, handles) as returned by app.ui.main_window.create_main_window
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # If the UI layer supports dependency injection for settings, prefer it.
    # Otherwise, fall back to a best-effort environment variable hint.
    kwargs: dict = {"expose_handles": True}
    if settings_path:
        kwargs["settings_path"] = settings_path
        kwargs["settings_file"] = settings_path
        kwargs["settings_yaml"] = settings_path
        try:
            import os
            os.environ["HANGUL_SETTINGS_PATH"] = settings_path
            os.environ["SETTINGS_PATH"] = settings_path
            os.environ["SETTINGS_FILE"] = settings_path
        except Exception:
            pass

    import inspect

    try:
        sig = inspect.signature(create_main_window)
        accepted = set(sig.parameters.keys())
        call_kwargs = {k: v for k, v in kwargs.items() if k in accepted}
    except Exception:
        call_kwargs = {"expose_handles": True}

    result = create_main_window(**call_kwargs)
    if isinstance(result, tuple) and len(result) == 2:
        window, handles = result
        return window, handles
    return result, None
from app.ui.widgets.segments import Characters

# --- Slow mode globals (module scope) ---
_slow_mode_enabled = False
_previous_wpm: int | None = None
_DEBUG_MAIN = False


# -------------------------------------------------
#           HELPERS
# -------------------------------------------------


# -------------------------------------------------
#          SETTINGS PERSISTENCE (TOP-LEVEL)
# -------------------------------------------------


# Detect if a segment contains any real glyph presenters
def _has_glyph_content(seg_w: Optional[QWidget]) -> bool:
    if seg_w is None:
        return False
    # If any Characters presenter exists inside, we consider it non-empty
    for w in seg_w.findChildren(QWidget):
        if isinstance(w, Characters):
            return True
    return False


def set_controls_for_repeats_locked(window: QWidget, locked: bool) -> None:
    """Enable/disable main controls during multi-repeat playback.

    Args:
        window: The main window instance.
        locked: If True, disable controls; if False, re-enable.
    """
    try:
        is_enabled = not bool(locked)

        # These objectNames are referenced by tests and by the UI.
        names = [
            "chipPronounce",
            "chipNext",
            "chipPrev",
            "chipSlow",
            "buttonNext",
            "buttonPrev",
            "comboMode",
        ]

        for name in names:
            try:
                w = cast(Optional[QWidget], window.findChild(QWidget, name))
                if w is not None:
                    w.setEnabled(is_enabled)
            except Exception:
                pass

    except Exception:
        # Never allow UI locking to crash tests or runtime.
        pass


# -------------------------------------------------
#           END HELPERS
# -------------------------------------------------


# --- Playback chip state management ---
class PlayChipState(Enum):
    PLAY = auto()
    REPEAT = auto()


current_chip_state = PlayChipState.PLAY


class BlockSegment:
    """One of the three segments inside a block container.

    This is a logical/structural class (no UI coupling). UI widgets that
    render the segment can attach later via composition.
    """

    def __init__(self, role: SegmentRole):
        if not isinstance(role, SegmentRole):
            raise TypeError("role must be a SegmentRole")
        self._role: SegmentRole = role

    @property
    def role(self) -> SegmentRole:
        return self._role


# -------------------------------------------------
#           DOMAIN-LOADED ORDERING
# -------------------------------------------------
# Canonical consonant/vowel ordering.
# Loaded from YAML via app/domain/jamo_data.py.
# main.py must not define or override ordering rules.
CONSONANT_ORDER: list[str] = get_consonant_order()
VOWEL_ORDER_BASIC10: list[str] = get_vowel_order_basic10()
VOWEL_ORDER_ADVANCED: list[str] = get_vowel_order_advanced()


class BlockManager:
    """Caches one BlockContainer per BlockType and preserves per-type state."""

    def show_consonant(self, stacked: QStackedWidget, consonant: str,
                       type_label: Optional[QLabel] = None, syll_label: Optional[QLabel] = None) -> None:
        # Use A_RightBranch container for a stable consonant-only view
        container = self._containers[BlockType.A_RightBranch]
        container.consonant_only(stacked, consonant)
        self._current_index = 0
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None:
            syll_label.setText(consonant)

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

    def attach_current(self, stacked: QStackedWidget, type_label: Optional[QLabel] = None,
                       syll_label: Optional[QLabel] = None) -> None:
        ctype = self.current_type()
        container = self._containers[ctype]
        container.attach(stacked)
        # [DEBUG] Print consonant/vowel/glyph from syllables right after attach
        try:
            _cons, _vowel, _glyph = select_syllable_for_block(ctype, prefer_consonant=u"ㄱ")
        except Exception:
            _cons = _vowel = _glyph = "?"
        if _DEBUG_MAIN:
            print(
                "[DEBUG] attach_current -> consonant/vowel from syllables: {0} / {1} glyph={2} block={3}".format(
                    _cons if "_cons" in locals() else "?",
                    _vowel if "_vowel" in locals() else "?",
                    _glyph if "_glyph" in locals() else "?",
                    ctype.name,
                )
            )
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        # Also set the composed glyph to the right-side label if provided
        if syll_label is not None and _glyph:
            syll_label.setText(_glyph)

    def show_pair(self, stacked: QStackedWidget, consonant: str, vowel: str,
                  type_label: Optional[QLabel] = None, syll_label: Optional[QLabel] = None) -> None:
        bt = block_type_for_pair(consonant, vowel)
        # Move index to match the target block type
        try:
            self._current_index = self._order.index(bt)
        except ValueError:
            self._current_index = 0
        container = self._containers[bt]
        # Prefer YAML glyph (if available later); fall back to Unicode composition
        glyph = compose_cv(consonant, vowel) or ""
        if _DEBUG_MAIN:
            print(
                "[DEBUG] show_pair -> consonant={0} vowel={1} glyph={2} block={3}".format(
                    consonant, vowel, glyph, bt.name
                )
            )
        container.attach(stacked, consonant=consonant, vowel=vowel, glyph=glyph)
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        if syll_label is not None and glyph:
            syll_label.setText(glyph)

    def next(self, stacked: QStackedWidget, type_label: Optional[QLabel] = None,
             syll_label: Optional[QLabel] = None) -> None:
        self._current_index = (self._current_index + 1) % len(self._order)
        self.attach_current(stacked, type_label, syll_label)

    def prev(self, stacked: QStackedWidget, type_label: Optional[QLabel] = None,
             syll_label: Optional[QLabel] = None) -> None:
        self._current_index = (self._current_index - 1) % len(self._order)
        self.attach_current(stacked, type_label, syll_label)


def main():
    app = QApplication(sys.argv)
    # Use the imported create_main_window from app.ui.main_window
    result = create_main_window(expose_handles=True)
    if isinstance(result, tuple) and len(result) == 2:
        window, _handles = result
    else:
        window, _handles = result, None
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
