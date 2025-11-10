import os
import sys
from enum import Enum
from typing import List, Optional, Callable, Tuple, cast
from abc import ABC, abstractmethod
from abc import ABCMeta  # ensure ABCMeta is available


import yaml
from PyQt6 import uic
from PyQt6.QtCore import QSize, Qt, QTimer, QPropertyAnimation, QEasingCurve, QObject
from PyQt6.QtGui import QFontMetrics, QAction, QIcon, QPixmap, QPainter, QPen, QColor
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QStackedWidget,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QSizePolicy,
    QSplitter,
    QRadioButton, QCheckBox,
    QToolBar,
)


# -------------------------------------------------
#           HELPERS
# -------------------------------------------------
# --- Syllable selection helpers (load from data/syllables.yaml) ---

def _project_root():
    return os.path.dirname(os.path.abspath(__file__))


def _load_syllables_yaml():
    path = os.path.join(_project_root(), "data", "syllables.yaml")
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data or {}


def select_syllable_for_block(block_type, prefer_consonant=u"ㄱ"):
    """
    Return (consonant, vowel, glyph) for the first syllable matching this block type.
    Prefer a specific consonant (default ㄱ) when available.
    Expects YAML items with keys: glyph, consonant, vowel, block_type (e.g. 'A_RightBranch').
    """
    data = _load_syllables_yaml()
    items = data.get("syllables", [])
    # BlockType enum likely has .name like "A_RightBranch"
    target_bt = getattr(block_type, "name", str(block_type))
    matches = [s for s in items if s.get("block_type") == target_bt]
    if not matches:
        # safe fallback: 아 (ㅇ+ㅏ) so we always render something
        return u"ㅇ", u"ㅏ", u"아"
    prefer = [s for s in matches if s.get("consonant") == prefer_consonant]
    chosen = prefer[0] if prefer else matches[0]
    return chosen.get("consonant"), chosen.get("vowel"), chosen.get("glyph")


def _vowel_labels_for_block(bt: BlockType) -> tuple[str, str]:
    suffix = {
        BlockType.A_RightBranch: "side-branching",
        BlockType.B_TopBranch: "top-branching",
        BlockType.C_BottomBranch: "bottom-branching",
        BlockType.D_Horizontal: "horizontal",
    }[bt]
    # Keep your existing bases exactly as-is
    base_title = SEG_TITLES["V"]  # "Medial"
    base_tip = SEG_TIPS["V"]  # "중성 (jungseong) → V "
    title = f"{base_title} — {suffix}"
    tip = f"{base_tip.strip()} ({suffix})"
    return title, tip

# Fits a single-line QLabel's font to its own rectangle using binary search
def _fit_label_font_to_label_rect(label: QLabel, min_pt: int = 24, max_pt: int = 160, padding: int = 10) -> None:
    text = label.text() or " "
    r = label.contentsRect()
    avail_w = max(1, r.width() - padding * 2)
    avail_h = max(1, r.height() - padding * 2)
    lo, hi = min_pt, max_pt
    best = lo
    while lo <= hi:
        mid = (lo + hi) // 2
        f = label.font()
        f.setPointSize(mid)
        fm = QFontMetrics(f)
        br = fm.tightBoundingRect(text)
        if br.width() <= avail_w and br.height() <= avail_h:
            best = mid
            lo = mid + 1
        else:
            hi = mid - 1
    f = label.font()
    f.setPointSize(best)
    label.setFont(f)

class _AutoFitHook(QObject):
    """Event filter to re-fit a label's font after its container resizes."""
    def __init__(self, target_label: QLabel, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._lbl = target_label

    def eventFilter(self, obj, ev):
        try:
            from PyQt6.QtCore import QEvent
            if ev.type() == QEvent.Type.Resize and self._lbl is not None:
                QTimer.singleShot(0, lambda: _fit_label_font_to_label_rect(
                    self._lbl, min_pt=48, max_pt=220, padding=6))
        except Exception:
            pass
        return False

# --- utility: deep-clear a container widget (layouts + stray children) ---
def _deep_clear_container(w: Optional[QWidget]) -> Optional[QVBoxLayout]:
    if w is None:
        return None
    lay = w.layout()
    if lay is None:
        lay = QVBoxLayout(w)
    # Drain this layout (widgets and nested layouts)
    while lay.count():
        it = lay.takeAt(0)
        if it is None:
            continue
        subw = it.widget()
        sublay = it.layout()
        if subw is not None:
            subw.setParent(None)
        if sublay is not None:
            while sublay.count():
                it2 = sublay.takeAt(0)
                if it2 is None:
                    continue
                sw2 = it2.widget()
                if sw2 is not None:
                    sw2.setParent(None)
    # Defensive: remove any direct children not managed by the layout
    for child in w.findChildren(QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly):
        child.setParent(None)
    lay.setContentsMargins(4, 4, 4, 4)
    lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return lay  # type: ignore

# Detect if a segment contains any real glyph presenters
def _has_glyph_content(seg_w: Optional[QWidget]) -> bool:
    if seg_w is None:
        return False
    # If any Characters presenter exists inside, we consider it non-empty
    for w in seg_w.findChildren(QWidget):
        if isinstance(w, Characters):
            return True
    return False

# If a segment has no glyph widget, add a centered muted placeholder (even if only subtitle present)
def _ensure_empty_placeholder(seg_w: Optional[QWidget]) -> None:
    if seg_w is None:
        return
    lay = seg_w.layout()
    if lay is None:
        lay = QVBoxLayout(seg_w)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)
    # If there is no glyph presenter inside, we treat it as visually empty
    if not _has_glyph_content(seg_w):
        # Avoid duplicate placeholders
        existing = seg_w.findChild(QLabel, "emptyPlaceholder", Qt.FindChildOption.FindChildrenRecursively)
        if existing is None:
            ph = QLabel("empty", seg_w)
            ph.setObjectName("emptyPlaceholder")
            f = ph.font()
            try:
                f.setItalic(True)
            except Exception:
                pass
            ph.setFont(f)
            ph.setStyleSheet("color: #888;")
            ph.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(ph, 1)

# -------------------------------------------------
#           END HELPERS
# -------------------------------------------------


class BlockType(Enum):
    """The four vowel-driven block layout templates."""
    A_RightBranch = 0
    B_TopBranch = 1
    C_BottomBranch = 2
    D_Horizontal = 3


class SegmentRole(Enum):
    """Three horizontal segments per block: top, middle, bottom."""
    Top = 0
    Middle = 1
    Bottom = 2


# --- Consonant position enum ---
class ConsonantPosition(Enum):
    Initial = 0
    Final = 1

# --- Study mode enum ---
class StudyMode(Enum):
    SYLLABLES = 1
    VOWELS = 2
    CONSONANTS = 3


class SegmentView(QWidget):
    """Lightweight presenter for a segment. Avoids object-name reliance.
    If a widget has a dynamic property 'segmentRole' set to 'Top'/'Middle'/'Bottom',
    we treat it as a SegmentView. Otherwise, this class can be instantiated
    and placed inside a container frame.
    """

    def __init__(self, parent=None, role: Optional[SegmentRole] = None):
        super().__init__(parent)
        self._role = role
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def set_role(self, role: SegmentRole) -> None:
        self._role = role

    def role(self) -> Optional[SegmentRole]:
        # Try dynamic property first so plain QFrames with property work too
        prop = self.property("segmentRole")
        if prop in ("Top", "Middle", "Bottom"):
            mapping = {
                "Top": SegmentRole.Top,
                "Middle": SegmentRole.Middle,
                "Bottom": SegmentRole.Bottom,
            }
            return mapping[prop]
        return self._role

class AutoFitLabel(QLabel):
    """A QLabel that auto-fits its font to fill itself (single-line)."""
    def __init__(self, text: str = "", parent: Optional[QWidget] = None,
                 min_pt: int = 18, max_pt: int = 72, padding: int = 6):
        super().__init__(text, parent)
        self._min_pt = min_pt
        self._max_pt = max_pt
        self._padding = padding
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sp)

    def setBounds(self, min_pt: int = None, max_pt: int = None, padding: int = None):
        if min_pt is not None:
            self._min_pt = int(min_pt)
        if max_pt is not None:
            self._max_pt = int(max_pt)
        if padding is not None:
            self._padding = int(padding)
        self._refit()

    def setText(self, text: str) -> None:
        super().setText(text)
        self._refit()

    def resizeEvent(self, ev) -> None:
        super().resizeEvent(ev)
        self._refit()

    def _refit(self) -> None:
        text = self.text() or " "
        r = self.contentsRect()
        avail_w = max(1, r.width() - self._padding * 2)
        avail_h = max(1, r.height() - self._padding * 2)
        lo, hi = self._min_pt, self._max_pt
        best = lo
        while lo <= hi:
            mid = (lo + hi) // 2
            f = self.font()
            f.setPointSize(mid)
            fm = QFontMetrics(f)
            br = fm.tightBoundingRect(text)
            if br.width() <= avail_w and br.height() <= avail_h:
                best = mid
                lo = mid + 1
            else:
                hi = mid - 1
        f = self.font()
        f.setPointSize(best)
        self.setFont(f)


# --- New presenter classes for consonant/vowel views ---


class _QtABCMeta(ABCMeta, type(QWidget)):
    """Combine ABCMeta with Qt's sip wrapper metaclass to allow abstract Qt widgets."""
    pass

# -------------------------------------------------
#           Abstract base for glyph presenters
# -------------------------------------------------
class Characters(QWidget, metaclass=_QtABCMeta):
    """Abstract base for glyph presenters (consonant/vowel).
    Provides: expanding size policy, vertical layout, AutoFitLabel glyph, and
    common setters/accessors. Subclasses should call super().__init__ and may
    add their own fields (e.g., position).
    """
    def __init__(self, parent: Optional[QWidget] = None,
                 grapheme: str = "",
                 ipa: Optional[str] = None,
                 *,
                 min_pt: int = 24,
                 max_pt: int = 128,
                 padding: int = 4) -> None:
        super().__init__(parent)
        self._grapheme = grapheme
        self._ipa = ipa
        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Allow the view itself to expand inside layouts
        sp_self = self.sizePolicy()
        sp_self.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp_self.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        self.setSizePolicy(sp_self)
        # Auto-fit glyph label (expands with its parent)
        self._glyph = AutoFitLabel(grapheme, self, min_pt=min_pt, max_pt=max_pt, padding=padding)
        layout.addWidget(self._glyph, 1)

    @abstractmethod
    def kind(self) -> str:
        """Return a discriminator for subclasses (e.g., 'consonant' or 'vowel').
        This abstract method makes Characters an ABC and prevents direct instantiation.
        """
        raise NotImplementedError

    # --- Common API ---
    def glyph_label(self) -> QLabel:
        return self._glyph

    def set_grapheme(self, g: str) -> None:
        self._grapheme = g
        self._glyph.setText(g)

    def set_ipa(self, ipa: Optional[str]) -> None:
        self._ipa = ipa


# --- Presenter for consonant view ---
class ConsonantView(Characters):
    def __init__(self, parent=None, grapheme: str = "", position: Optional[ConsonantPosition] = None,
                 ipa: Optional[str] = None):
        super().__init__(parent, grapheme=grapheme, ipa=ipa, min_pt=24, max_pt=128, padding=4)
        self._position = position

    # Preserve setter used elsewhere
    def set_position(self, p: ConsonantPosition) -> None:
        self._position = p

    def kind(self) -> str:
        return "consonant"


# --- Presenter for vowel view ---
class VowelView(Characters):
    def __init__(self, parent=None, grapheme: str = "", ipa: Optional[str] = None):
        super().__init__(parent, grapheme=grapheme, ipa=ipa, min_pt=24, max_pt=128, padding=4)

    def kind(self) -> str:
        return "vowel"


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


class BlockContainer:
    """Holds one block type (A–D) and exactly three BlockSegments.

    Invariant:
      - Must be constructed with a non-null BlockType.
      - Owns exactly three segments: Top, Middle, Bottom (in that order).
    """

    def __init__(self, block_type: BlockType):
        if block_type is None or not isinstance(block_type, BlockType):
            raise ValueError("BlockContainer requires a valid BlockType")
        self._type: BlockType = block_type
        self._segments: List[BlockSegment] = [
            BlockSegment(SegmentRole.Top),
            BlockSegment(SegmentRole.Middle),
            BlockSegment(SegmentRole.Bottom),
        ]

    @property
    def type(self) -> BlockType:
        return self._type

    @property
    def segments(self) -> List[BlockSegment]:
        # Return a shallow copy to preserve internal ordering/size.
        return list(self._segments)

    def segment(self, role: SegmentRole) -> BlockSegment:
        if role == SegmentRole.Top:
            return self._segments[0]
        if role == SegmentRole.Middle:
            return self._segments[1]
        if role == SegmentRole.Bottom:
            return self._segments[2]
        raise KeyError("Unknown SegmentRole: {}".format(role))

    def attach(self, stacked: QStackedWidget,
               consonant: Optional[str] = None,
               vowel: Optional[str] = None,
               glyph: Optional[str] = None) -> None:
        """Attach this container to the UI: select the correct page, clear frames, and
        insert fresh presenters for each segment. This reuses the existing pages
        (A–D) in jamo.ui and only swaps inner content per switch.
        """
        if not isinstance(stacked, QStackedWidget):
            raise TypeError("stacked must be a QStackedWidget")

        # Map BlockType to stacked index
        type_to_index = {
            BlockType.A_RightBranch: 0,
            BlockType.B_TopBranch: 1,
            BlockType.C_BottomBranch: 2,
            BlockType.D_Horizontal: 3,
        }
        index = type_to_index.get(self._type)
        if index is None:
            raise KeyError("Unknown BlockType: {}".format(self._type))

        # Switch the current page
        stacked.setCurrentIndex(index)
        page = stacked.widget(index)
        if page is None:
            raise RuntimeError("Stacked page {} not found".format(index))

        # Preferred: discover 3 segments by role (no object-name reliance)
        # Strategy A: find promoted SegmentView children and map by their role()
        views = [w for w in page.findChildren(QWidget) if isinstance(w, SegmentView)]
        role_to_widget = {}
        for v in views:
            r = v.role()
            if r is not None:
                role_to_widget[r] = v

        # Strategy B: find any QWidget with dynamic property 'segmentRole'
        if len(role_to_widget) < 3:
            for w in page.findChildren(QWidget):
                prop = w.property("segmentRole")
                if prop in ("Top", "Middle", "Bottom"):
                    mapping = {
                        "Top": SegmentRole.Top,
                        "Middle": SegmentRole.Middle,
                        "Bottom": SegmentRole.Bottom,
                    }
                    role_to_widget[mapping[prop]] = w

        # Fallback C: legacy per-type frame names
        if len(role_to_widget) < 3:
            type_prefix = {
                BlockType.A_RightBranch: "typeA_",
                BlockType.B_TopBranch: "typeB_",
                BlockType.C_BottomBranch: "typeC_",
                BlockType.D_Horizontal: "typeD_",
            }[self._type]
            wanted_names = {
                SegmentRole.Top: type_prefix + "segmentTop",
                SegmentRole.Middle: type_prefix + "segmentMiddle",
                SegmentRole.Bottom: type_prefix + "segmentBottom",
            }
            for role, objname in wanted_names.items():
                w = page.findChild(QWidget, objname, Qt.FindChildOption.FindChildrenRecursively)
                if w is not None:
                    role_to_widget[role] = w
                print("[DEBUG] {}: lookup {} -> {}".format(
                    page.objectName(), objname, "OK" if isinstance(w, QWidget) else "MISSING"
                ))

        # As a last resort, if a role is still missing, create a SegmentView and add it to the page's top/middle/bottom rows
        # (requires a QGridLayout with rows 0,1,2). If not present, we skip creation to avoid guessing.
        if len(role_to_widget) < 3:
            grid = page.layout()
            if isinstance(grid, QVBoxLayout):
                pass  # not attempting to inject into unfamiliar layouts
            else:
                try:
                    # best-effort: rows 0..2, col 0
                    for role, row in ((SegmentRole.Top, 0), (SegmentRole.Middle, 1), (SegmentRole.Bottom, 2)):
                        if role not in role_to_widget:
                            sv = SegmentView(page, role)
                            layout = sv.layout()
                            if layout is None:
                                layout = QVBoxLayout(sv)
                            layout.setContentsMargins(4, 4, 4, 4)
                            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                            role_to_widget[role] = sv
                except Exception:
                    pass

        try:
            jw = stacked.parentWidget().size().width() if stacked.parentWidget() else 0
            jh = stacked.parentWidget().size().height() if stacked.parentWidget() else 0
            print(f"[DEBUG] after-attach sizes -> page={page.size().width()}x{page.size().height()} jamo={jw}x{jh}")
        except Exception:
            pass


        # --- Orthographic presenters using ConsonantView / VowelView ---
        def _ensure_cleared_layout(w: QWidget) -> QVBoxLayout:
            layout = w.layout()
            if layout is None:
                layout = QVBoxLayout(w)
            # clear
            while layout.count():
                item = layout.takeAt(0)
                ww = item.widget()
                if ww is not None:
                    ww.setParent(None)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            return layout  # type: ignore

        def _add_row(parent_w: QWidget, widgets: List[QWidget]) -> None:
            row_holder = QWidget(parent_w)
            row = QHBoxLayout(row_holder)
            row.setContentsMargins(0, 0, 0, 0)
            row.setSpacing(25)  # increase spacing between consonant and vowel to 25px
            # row.setAlignment(Qt.AlignmentFlag.AlignCenter)
            for wdg in widgets:
                # Give each column equal stretch so it fills available width
                row.addWidget(wdg, 1)
            parent_layout = parent_w.layout()
            if parent_layout is None:
                parent_layout = QVBoxLayout(parent_w)
                parent_layout.setContentsMargins(4, 4, 4, 4)
                parent_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            parent_layout.addWidget(row_holder)

        # Default demo glyphs (can be replaced later by real content)
        # Pick a concrete CV from syllables.yaml for this block type (prefer ㄱ if present)
        if consonant is not None and vowel is not None:
            cons_char, vowel_char = consonant, vowel
            _glyph = glyph or (compose_cv(consonant, vowel) or "")
        else:
            cons_char, vowel_char, _glyph = select_syllable_for_block(self._type, prefer_consonant=u"ㄱ")

        # Resolve target widgets for roles
        top_w = role_to_widget.get(SegmentRole.Top)
        mid_w = role_to_widget.get(SegmentRole.Middle)
        bot_w = role_to_widget.get(SegmentRole.Bottom)

        # --- Deep segment debug ---
        def _dbg_seg(w: Optional[QWidget], name: str):
            try:
                layout = w.layout() if w is not None else None
                cnt = layout.count() if layout is not None else -1
                sz = w.size() if w is not None else QSize(0, 0)
                print(f"[DEBUG] seg {name}: exists={w is not None} size={sz.width()}x{sz.height()} "
                      f"layout={type(layout).__name__ if layout else None} items={cnt}")
            except Exception as e:
                print(f"[DEBUG] seg {name}: error={e}")

        _dbg_seg(top_w, "Top")
        _dbg_seg(mid_w, "Middle")
        _dbg_seg(bot_w, "Bottom")


        # Clear and place presenters per type
        if top_w is not None:
            _deep_clear_container(top_w)
        if mid_w is not None:
            _deep_clear_container(mid_w)
        if bot_w is not None:
            _deep_clear_container(bot_w)

        # TYPE A
        if self._type == BlockType.A_RightBranch:
            # Top: L (left) + V (right) with per-glyph subtitles
            if top_w is not None:
                cons = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                cons.setToolTip(SEG_TIPS["L"])  # Leading consonant
                vow = VowelView(top_w, vowel_char)
                vow.setToolTip(SEG_TIPS["V"])  # Medial vowel
                colL = _make_labeled_column("L", cons, top_w)
                v_title, v_tip = _vowel_labels_for_block(self._type)
                colV = _make_labeled_column_custom(v_title, v_tip, vow, top_w)
                _add_row(top_w, [colL, colV])

                # Ensure the vowel isn't visually narrower than consonant or its title
                def _enforce_a():
                    try:
                        _, cons_lbl = _extract_title_and_glyph(colL)
                        v_title, v_lbl = _extract_title_and_glyph(colV)
                        cons_w = cons_lbl.width() if cons_lbl else 0
                        v_title_w = v_title.sizeHint().width() if v_title else 0
                        want = max(cons_w, v_title_w)
                        if v_lbl:
                            v_lbl.setMinimumWidth(want)
                            v_lbl.update()
                    except Exception:
                        pass

                QTimer.singleShot(0, _enforce_a)
            # Middle: empty (by design)
            # Bottom: empty (no T)
            if bot_w is not None:
                bot_layout = bot_w.layout()
                bot_layout.setContentsMargins(4, 4, 4, 4)
                bot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                bot_layout.addWidget(_mk_title_label(SEG_TITLES["T"], SEG_TIPS["T"], bot_w))

        # TYPE B
        elif self._type == BlockType.B_TopBranch:
            # Top: V (with contextual subtitle); Middle: L (with subtitle)
            if top_w is not None:
                v_top = VowelView(top_w, vowel_char)
                v_top.setToolTip(SEG_TIPS["V"])  # base tooltip
                v_title, v_tip = _vowel_labels_for_block(self._type)  # ← adds “top-branching”
                colV_top = _make_labeled_column_custom(v_title, v_tip, v_top, top_w)
                top_w.layout().addWidget(colV_top)

            if mid_w is not None:
                c_mid = ConsonantView(mid_w, cons_char, ConsonantPosition.Initial)
                c_mid.setToolTip(SEG_TIPS["L"])  # Leading consonant
                colL_mid = _make_labeled_column("L", c_mid, mid_w)
                mid_w.layout().addWidget(colL_mid)

            # Ensure the vowel (top) isn't narrower than its own title
            def _enforce_b():
                try:
                    v_title_lbl, v_glyph_lbl = _extract_title_and_glyph(colV_top)
                    want = v_title_lbl.sizeHint().width() if v_title_lbl else 0
                    if v_glyph_lbl:
                        v_glyph_lbl.setMinimumWidth(want)
                        v_glyph_lbl.update()
                except Exception:
                    pass

            QTimer.singleShot(0, _enforce_b)

            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                bot_layout = bot_w.layout()
                bot_layout.setContentsMargins(4, 4, 4, 4)
                bot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                bot_layout.addWidget(_mk_title_label(SEG_TITLES["T"], SEG_TIPS["T"], bot_w))

        elif self._type == BlockType.C_BottomBranch:
            # Top: L (with subtitle); Middle: V (with subtitle)
            if top_w is not None:
                c_top = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                c_top.setToolTip(SEG_TIPS["L"])  # Leading consonant
                colL_top = _make_labeled_column("L", c_top, top_w)
                top_w.layout().addWidget(colL_top)
            if mid_w is not None:
                v_mid = VowelView(mid_w, vowel_char)
                v_mid.setToolTip(SEG_TIPS["V"])
                v_title, v_tip = _vowel_labels_for_block(self._type)
                colV_mid = _make_labeled_column_custom(v_title, v_tip, v_mid, mid_w)
                mid_w.layout().addWidget(colV_mid)
            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                bot_layout = bot_w.layout()
                bot_layout.setContentsMargins(4, 4, 4, 4)
                bot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                bot_layout.addWidget(_mk_title_label(SEG_TITLES["T"], SEG_TIPS["T"], bot_w))

        elif self._type == BlockType.D_Horizontal:
            # Top: L (with subtitle); Middle: V (with subtitle)
            if top_w is not None:
                c_top = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                c_top.setToolTip(SEG_TIPS["L"])  # Leading consonant
                colL_top = _make_labeled_column("L", c_top, top_w)
                top_w.layout().addWidget(colL_top)
            if mid_w is not None:
                v_mid = VowelView(mid_w, vowel_char)
                v_mid.setToolTip(SEG_TIPS["V"])
                v_title, v_tip = _vowel_labels_for_block(self._type)
                colV_mid = _make_labeled_column_custom(v_title, v_tip, v_mid, mid_w)
                mid_w.layout().addWidget(colV_mid)
            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                bot_layout = bot_w.layout()
                bot_layout.setContentsMargins(4, 4, 4, 4)
                bot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                bot_layout.addWidget(_mk_title_label(SEG_TITLES["T"], SEG_TIPS["T"], bot_w))

        _ensure_empty_placeholder(top_w)
        _ensure_empty_placeholder(mid_w)
        _ensure_empty_placeholder(bot_w)
        _enforce_equal_segment_heights(page, top_w, mid_w, bot_w)
        page.updateGeometry()
        page.update()

    def consonant_only(self, stacked: QStackedWidget, consonant: str) -> None:
        # Force Type A layout for a simple, stable presentation
        index = 0  # A_RightBranch is page 0 by design
        stacked.setCurrentIndex(index)
        page = stacked.widget(index)
        if page is None:
            raise RuntimeError("Stacked page 0 not found")
        # Discover segments (same fallbacks as attach):
        role_to_widget = {}
        # A) promoted SegmentView children with explicit role()
        views = [w for w in page.findChildren(QWidget) if isinstance(w, SegmentView)]
        for v in views:
            r = v.role()
            if r is not None:
                role_to_widget[r] = v
        # B) dynamic property "segmentRole"
        if len(role_to_widget) < 3:
            for w in page.findChildren(QWidget):
                prop = w.property("segmentRole")
                if prop in ("Top", "Middle", "Bottom"):
                    mapping = {"Top": SegmentRole.Top, "Middle": SegmentRole.Middle, "Bottom": SegmentRole.Bottom}
                    role_to_widget[mapping[prop]] = w
        # C) legacy per-type frame names
        if len(role_to_widget) < 3:
            type_prefix = "typeA_"  # consonant-only uses the Type A page
            wanted_names = {
                SegmentRole.Top: type_prefix + "segmentTop",
                SegmentRole.Middle: type_prefix + "segmentMiddle",
                SegmentRole.Bottom: type_prefix + "segmentBottom",
            }
            for role, objname in wanted_names.items():
                w = page.findChild(QWidget, objname, Qt.FindChildOption.FindChildrenRecursively)
                if w is not None:
                    role_to_widget[role] = w
        top_w = role_to_widget.get(SegmentRole.Top)
        mid_w = role_to_widget.get(SegmentRole.Middle)
        bot_w = role_to_widget.get(SegmentRole.Bottom)
        # Clear any existing layouts/widgets
        top_lay = _deep_clear_container(top_w)
        _deep_clear_container(mid_w)  # ensure any prior vowel is gone
        bot_lay = _deep_clear_container(bot_w)

        # Add title + consonant glyph in top
        if top_lay is not None:
            cons = ConsonantView(top_w, consonant, ConsonantPosition.Initial)
            cons.setToolTip(SEG_TIPS["L"])  # Leading consonant
            col = _make_labeled_column("L", cons, top_w)
            top_lay.addWidget(col, 1)
        # Bottom: T subtitle only (no glyph)
        if bot_lay is not None:
            bot_lay.addWidget(_mk_title_label(SEG_TITLES["T"], SEG_TIPS["T"], bot_w))
        _ensure_empty_placeholder(top_w)
        _ensure_empty_placeholder(mid_w)
        _ensure_empty_placeholder(bot_w)
        _enforce_equal_segment_heights(page, top_w, mid_w, bot_w)
        page.updateGeometry(); page.update()


# Map vowel to block type (basic set)
VOWEL_TO_BLOCK = {
    # A — Right-branching
    "ㅏ": BlockType.A_RightBranch, "ㅑ": BlockType.A_RightBranch,
    "ㅓ": BlockType.A_RightBranch, "ㅕ": BlockType.A_RightBranch,
    "ㅣ": BlockType.A_RightBranch,
    # B — Top-branching
    "ㅗ": BlockType.B_TopBranch, "ㅛ": BlockType.B_TopBranch,
    # C — Bottom-branching
    "ㅜ": BlockType.C_BottomBranch, "ㅠ": BlockType.C_BottomBranch,
    # D — Horizontal
    "ㅡ": BlockType.D_Horizontal,
}

# Basic 10 vowel order (fallback; will later load from YAML)
VOWEL_ORDER_BASIC10 = ["ㅏ", "ㅑ", "ㅓ", "ㅕ", "ㅗ", "ㅛ", "ㅜ", "ㅠ", "ㅡ", "ㅣ"]

# Unicode CV composer (no final consonant) as a safe fallback
_CHOESONG = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
_JUNGSUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ",
             "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
_DEF_L = {ch: i for i, ch in enumerate(_CHOESONG)}
_DEF_V = {ch: i for i, ch in enumerate(_JUNGSUNG)}


def compose_cv(consonant: str, vowel: str) -> Optional[str]:
    try:
        L = _DEF_L[consonant]
        V = _DEF_V[vowel]
        code = 0xAC00 + ((L * 21) + V) * 28  # T=0 (no final)
        return chr(code)
    except Exception:
        return None


# -------------------------------------------------
#           ICON HELPERS
# -------------------------------------------------

def build_hamburger_icon(size: int = 24, thickness: int = 2, margin: int = 4) -> QIcon:
    """Create a simple hamburger icon (three horizontal lines) as a QIcon.
    Drawn at runtime to avoid bundling assets.
    """
    pm = QPixmap(size, size)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    try:
        pen = QPen(QColor(30, 30, 30))
        pen.setWidth(thickness)
        p.setPen(pen)
        y1 = margin
        y2 = size // 2
        y3 = size - margin
        x1 = margin
        x2 = size - margin
        p.drawLine(x1, y1, x2, y1)
        p.drawLine(x1, y2, x2, y2)
        p.drawLine(x1, y3, x2, y3)
    finally:
        p.end()
    return QIcon(pm)


# --- Segment subtitles (Korean ↔ L/V/T) ---
SEG_TITLES = {
    "L": "Leading consonant",
    "V": "Vowel",
    "T": "Trailing consonant",
}

SEG_TIPS = {
    "L": "초성 (choseong) → L ",
    "V": "중성 (jungseong) → V ",
    "T": "종성 (jongseong) → T",
}


def _mk_title_label(text: str, tooltip: str, parent: QWidget) -> QLabel:
    lbl = QLabel(text, parent)
    f = lbl.font()
    f.setPointSize(max(10, f.pointSize()))
    f.setBold(True)
    lbl.setFont(f)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setToolTip(tooltip)
    return lbl

# Ensure the three segment containers in a page get equal vertical space
from PyQt6.QtWidgets import QSizePolicy as _QSizePolicyAlias

def _enforce_equal_segment_heights(page: QWidget,
                                   top_w: Optional[QWidget],
                                   mid_w: Optional[QWidget],
                                   bot_w: Optional[QWidget]) -> None:
    layout = page.layout()
    if not isinstance(layout, QVBoxLayout):
        return
    for w in (top_w, mid_w, bot_w):
        if w is None:
            continue
        # make each segment vertically expanding
        sp = w.sizePolicy()
        sp.setVerticalPolicy(_QSizePolicyAlias.Policy.Expanding)
        w.setSizePolicy(sp)
        # ensure equal stretch in the page's vertical layout
        idx = layout.indexOf(w)
        if idx != -1:
            layout.setStretch(idx, 1)

# Center a subtitle directly above a single glyph widget
def _make_labeled_column(key: str, widget: QWidget, parent: QWidget) -> QWidget:
    col = QWidget(parent)
    v = QVBoxLayout(col)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)
    v.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(_mk_title_label(SEG_TITLES[key], SEG_TIPS[key], col))
    v.addWidget(widget, 1)
    return col


# Same as _make_labeled_column but with explicit title/tooltip overrides
def _make_labeled_column_custom(title: str, tip: str, widget: QWidget, parent: QWidget) -> QWidget:
    col = QWidget(parent)
    v = QVBoxLayout(col)
    v.setContentsMargins(0, 0, 0, 0)
    v.setSpacing(4)
    v.setAlignment(Qt.AlignmentFlag.AlignCenter)
    v.addWidget(_mk_title_label(title, tip, col))
    v.addWidget(widget, 1)
    return col

def _extract_title_and_glyph(column_widget: QWidget) -> Tuple[Optional[QLabel], Optional[QLabel]]:
    title = None
    glyph = None
    if column_widget is None:
        return title, glyph
    labels = column_widget.findChildren(QLabel)
    if labels:
        # Heuristic: first label is the title; last label is the glyph (AutoFitLabel is a QLabel)
        title = labels[0]
        glyph = labels[-1]
    return title, glyph


class BlockManager:
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
    """Caches one BlockContainer per BlockType and preserves per-type state."""

    def __init__(self):
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

    def current_type(self):
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
        print(
            f"[DEBUG] attach_current -> consonant/vowel from syllables: {_cons if '_cons' in locals() else '?'} / {_vowel if '_vowel' in locals() else '?'} glyph={_glyph if '_glyph' in locals() else '?'} block={ctype.name}")
        if type_label is not None:
            type_label.setText(self._names[self._current_index])
        # Also set the composed glyph to the right-side label if provided
        if syll_label is not None and _glyph:
            syll_label.setText(_glyph)

    def show_pair(self, stacked: QStackedWidget, consonant: str, vowel: str,
                  type_label: Optional[QLabel] = None, syll_label: Optional[QLabel] = None) -> None:
        bt = VOWEL_TO_BLOCK.get(vowel, self.current_type())
        # Move index to match the target block type
        try:
            self._current_index = self._order.index(bt)
        except ValueError:
            self._current_index = 0
        container = self._containers[bt]
        # Prefer YAML glyph (if available later); fall back to Unicode composition
        glyph = compose_cv(consonant, vowel) or ""
        print(f"[DEBUG] show_pair -> consonant={consonant} vowel={vowel} glyph={glyph} block={bt.name}")
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


class JamoBlock(QWidget):
    """A simple container that enforces a 1:1 aspect ratio for its contents.
    Place the real JamoBlock inside this widget so it always renders as a square.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._inner_layout = QVBoxLayout(self)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setSpacing(0)
        sp = self.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp.setVerticalPolicy(QSizePolicy.Policy.Preferred)
        sp.setHeightForWidth(True)
        self.setSizePolicy(sp)
        self._inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._container: Optional[BlockContainer] = None

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, w: int) -> int:
        return w  # 1:1 aspect ratio

    def sizeHint(self) -> QSize:
        return QSize(400, 400)

    def minimumSizeHint(self) -> QSize:
        return QSize(200, 200)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        item = self._inner_layout.itemAt(0)
        if item is None:
            return
        child = item.widget()
        if child is None:
            return
        side = min(self.width(), self.height())
        # Center the square by adjusting margins
        left = (self.width() - side) // 2
        top = (self.height() - side) // 2
        self._inner_layout.setContentsMargins(left, top, left, top)
        # Enforce square size for the child
        child.setMinimumSize(side, side)
        child.setMaximumSize(side, side)

    def setContainer(self, container: BlockContainer) -> None:
        """Attach a BlockContainer to this JamoBlock (replaces any existing)."""
        if not isinstance(container, BlockContainer):
            raise TypeError("container must be a BlockContainer")
        self._container = container

    def container(self) -> Optional[BlockContainer]:
        """Return the attached BlockContainer, if any."""
        return self._container



    # -------------------------------------------------
    #           PROGRESSION (Scaffolding only)
    # -------------------------------------------------


from dataclasses import dataclass


class ProgressionMode(Enum):
    """Two progression paths: consonant→vowel or vowel→consonant."""
    CONSONANT_TO_VOWEL = "C→V"
    VOWEL_TO_CONSONANT = "V→C"


class PairStatus(Enum):
    """Status tags for CV pairs loaded from YAML (see syllables.yaml / overrides)."""
    ALLOWED = "allowed"
    RARE = "rare"
    NOT_USED = "not_used"
    IMPOSSIBLE = "impossible"


@dataclass(frozen=True)
class ProgressionStep:
    consonant: str  # e.g., "ㄱ"
    vowel: str  # e.g., "ㅏ"
    glyph: str  # e.g., "가"
    block_type: str  # "A_RightBranch" | "B_TopBranch" | "C_BottomBranch" | "D_Horizontal"
    status: PairStatus  # from YAML
    index_c: int  # consonant index in current order
    index_v: int  # vowel index in current order


@dataclass
class ProgressionState:
    mode: ProgressionMode
    index_c: int = 0
    index_v: int = 0
    anchor_c: Optional[str] = None  # fixed consonant when mode is C→V
    anchor_v: Optional[str] = None  # fixed vowel when mode is V→C
    include_rare: bool = False
    use_advanced_vowels: bool = False  # toggle to include complex vowels


class ProgressionController:
    """Pure logic (UI-agnostic). Drives next/prev selection through CV space.
    NOTE: This is a non-functional scaffold; method bodies are intentionally empty.
    """

    def __init__(self,
                 consonant_order: List[str],
                 vowel_order_basic: List[str],
                 vowel_order_adv: List[str],
                 syllable_lookup: "Callable[[str, str], Tuple[str, str, str, str, PairStatus]]",
                 state: Optional[ProgressionState] = None) -> None:
        # TODO: store parameters, choose active vowel order depending on state.use_advanced_vowels
        pass

    def set_mode(self, mode: ProgressionMode) -> None:
        pass

    def set_anchor_consonant(self, c: str) -> None:
        pass

    def set_anchor_vowel(self, v: str) -> None:
        pass

    def set_include_rare(self, include: bool) -> None:
        pass

    def set_use_advanced_vowels(self, use_adv: bool) -> None:
        pass

    def reset(self) -> None:
        pass

    def current(self) -> ProgressionStep:
        # TODO: return the current step without advancing
        raise NotImplementedError

    def next(self) -> ProgressionStep:
        # TODO: advance according to mode, skipping IMPOSSIBLE and (optionally) RARE
        raise NotImplementedError

    def prev(self) -> ProgressionStep:
        # TODO: reverse-advance according to mode
        raise NotImplementedError

    def progress_summary(self) -> str:
        # TODO: e.g., "5/10 vowels" or "8/19 consonants" depending on mode
        return ""

    # --- YAML adapter (no implementation) ---
    # These constants should ultimately be loaded from data/*.yaml.
    # If you want me to add them now, switch to those files and I will insert order arrays.
    CONSONANT_ORDER_DEFAULT: List[str] = []  # e.g., ["ㄱ","ㄲ","ㄴ", ...]
    VOWEL_ORDER_BASIC10: List[str] = []  # e.g., ["ㅏ","ㅑ","ㅓ","ㅕ","ㅗ","ㅛ","ㅜ","ㅠ","ㅡ","ㅣ"]
    VOWEL_ORDER_ADV: List[str] = []  # e.g., ["ㅐ","ㅔ","ㅘ", ...]

    def syllable_lookup_adapter(consonant: str, vowel: str):
        """Return (cons, vowel, glyph, block_type, status) for a CV pair.
        Placeholder only; will read from syllables.yaml and overrides when implemented.
        """
        raise NotImplementedError

    # --- UI wiring placeholders (no-op) ---
    # When ready, we will:
    #  - create a ProgressionController with the orders and adapter
    #  - wire Next/Prev to controller.next()/prev()
    #  - wire a mode selector + anchor pickers
    #  - call BlockManager + set the big glyph from ProgressionStep
    # For now, leaving the existing behavior untouched.


def main():
    app = QApplication(sys.argv)

    # Load the main window UI
    window = uic.loadUi("ui/form.ui")

    # Ensure the menubar is shown inside the window (macOS uses system bar by default)
    try:
        menubar = window.findChild(QWidget, "menubar")
        if menubar is not None and hasattr(menubar, "setNativeMenuBar"):
            menubar.setNativeMenuBar(False)
        # Wire the menu action to toggle the drawer
        action_toggle = window.findChild(QAction, "actionToggleDrawer")
        if action_toggle is not None:
            action_toggle.triggered.connect(lambda: _toggle_drawer() if ' _toggle_drawer' in globals() else None)
    except Exception:
        pass

    # Hamburger + Drawer wiring (left drawer panel is hidden by default in UI)
    button_hamburger = window.findChild(QPushButton, "buttonHamburger") or window.findChild(QWidget, "buttonHamburger")
    drawer_left = window.findChild(QWidget, "drawerLeft")

    # Ensure drawer has a known collapsed state if hidden
    if drawer_left is not None and not drawer_left.isVisible():
        drawer_left.setMaximumHeight(0)

    # Load the Jamo block UI (widget with QStackedWidget inside)
    jamo_block = uic.loadUi("ui/jamo.ui")  # expected root: QWidget named JamoBlock

    # Create a square container and place the JamoBlock inside it
    square = JamoBlock()
    square._inner_layout.addWidget(jamo_block)

    # Place the square Jamo block into the splitter's left pane (replacing placeholder)
    splitter = window.findChild(QSplitter, "splitJamoAndGlyph")
    if splitter is None:
        print("[ERROR] QSplitter 'splitJamoAndGlyph' not found in form.ui", file=sys.stderr)
        window.show()
        sys.exit(app.exec())

    placeholder = splitter.findChild(QWidget, "JamoBlock")
    if placeholder is None:
        print("[ERROR] Placeholder 'JamoBlock' not found under splitter", file=sys.stderr)
        window.show()
        sys.exit(app.exec())

    idx = splitter.indexOf(placeholder)
    if idx == -1:
        idx = 0
    # Keep object name consistent for stylesheet/lookup
    square.setObjectName("JamoBlock")
    splitter.insertWidget(idx, square)
    # Remove old placeholder widget
    placeholder.setParent(None)
    placeholder.deleteLater()

    # Defer initial splitter sizing to the next event loop tick so geometry is valid
    def _init_splitter_sizes():
        try:
            sw = splitter.width() or window.width()
            left = max(260, int(sw * 0.60))
            right = max(300, sw - left)
            splitter.setStretchFactor(0, 1)   # let left grow
            splitter.setStretchFactor(1, 1)
            splitter.setCollapsible(0, False)
            splitter.setCollapsible(1, False)
            splitter.setSizes([left, right])
            # Red debug borders: outer Jamo square and segment frames via dynamic property
            try:
                jamo_block.setStyleSheet(
                    """
                    #JamoBlock { border: 3px solid red; }
                    QWidget[segmentRole="Top"], QWidget[segmentRole="Middle"], QWidget[segmentRole="Bottom"] {
                        border: 1px dashed red;
                    }
                    """
                )
            except Exception as e:
                print(f"[WARN] stylesheet failed: {e}")
            square.show(); jamo_block.show()
            print(f"[DEBUG] splitter init sizes -> {splitter.sizes()}")
        except Exception as e:
            print(f"[WARN] splitter init failed: {e}")

    square.setMinimumSize(220, 220)
    QTimer.singleShot(0, _init_splitter_sizes)

    # Ensure there is a large glyph label to the right of the block
    syll_label = window.findChild(QLabel, "labelSyllableRight")
    right_container = window.findChild(QWidget, "syllableContainer")
    if right_container is not None:
        sp = right_container.sizePolicy()
        sp.setHorizontalPolicy(QSizePolicy.Policy.Preferred)
        sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        right_container.setSizePolicy(sp)
        right_container.setMinimumWidth(240)

    # Make the big glyph label fill its container
    if syll_label is not None:
        sp_lbl = syll_label.sizePolicy()
        sp_lbl.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        sp_lbl.setVerticalPolicy(QSizePolicy.Policy.Expanding)
        syll_label.setSizePolicy(sp_lbl)
        syll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Prefer no word wrap for max size; single-line glyph
        try:
            syll_label.setWordWrap(False)
        except Exception:
            pass
        # Give the label stretch within its parent layout
        try:
            rc_layout = right_container.layout() if right_container is not None else None
            if rc_layout is not None:
                idx = rc_layout.indexOf(syll_label)
                if idx != -1:
                    rc_layout.setStretch(idx, 1)
        except Exception:
            pass

    # Install auto-fit hook for right panel resize
    if right_container is not None and syll_label is not None:
        try:
            hook = _AutoFitHook(syll_label, right_container)
            # Keep a reference to avoid GC
            right_container._auto_fit_hook = hook
            right_container.installEventFilter(hook)
        except Exception as e:
            print(f"[WARN] auto-fit hook not installed: {e}")

    def _update_layout_sizes():
        # Maintain a 60/40 split of the splitter width
        sw = splitter.width() or window.width()
        left_target = max(260, int(sw * 0.60))
        right_target = max(300, sw - left_target)
        splitter.setSizes([left_target, right_target])

        # Square side is driven by the left pane's width; only cap by right height if sensible
        side_by_width = left_target
        side = side_by_width
        rh = 0
        try:
            rh = right_container.height() if right_container is not None else 0
        except Exception:
            rh = 0
        if rh >= 220:
            side = min(side_by_width, rh)
        elif rh > 0:
            print(f"[WARN] right_container height too small ({rh}); not capping Jamo square")

        square.setFixedSize(side, side)

        # Defer font-fit so label has final rect after splitter moves
        if syll_label is not None:
            QTimer.singleShot(0, lambda: _fit_label_font_to_label_rect(
                syll_label, min_pt=48, max_pt=220, padding=6
            ))

        # Debug
        try:
            lw = square.width()
            lh = square.height()
            rw = right_container.width() if right_container is not None else -1
            rh2 = right_container.height() if right_container is not None else -1
            print(f"[DEBUG] sizes(update) -> jamo={lw}x{lh} right={rw}x{rh2} splitter={splitter.sizes()}")
        except Exception:
            pass
        try:
            print(f"[DEBUG] splitter(sizes-end) -> {splitter.sizes()}")
        except Exception:
            pass
    # Also re-fit the big glyph label when the splitter moves
    try:
        splitter.splitterMoved.connect(lambda pos, idx: (
            QTimer.singleShot(0, lambda: _fit_label_font_to_label_rect(syll_label, min_pt=48, max_pt=220, padding=6))
            if syll_label is not None else None
        ))
    except Exception:
        pass

    # Get the stacked widget that contains the 4 block-type pages
    stacked = jamo_block.findChild(QStackedWidget, "stackedTemplates")
    if stacked is None:
        print("[ERROR] QStackedWidget 'stackedTemplates' not found in jamo.ui", file=sys.stderr)
        window.show()
        sys.exit(app.exec())

    # Default to pageRightBranch when the app opens (index 0 by design)
    stacked.setCurrentIndex(0)

    type_label = window.findChild(QLabel, "labelBlockType")
    manager = BlockManager()
    # Temporary progression state (until ProgressionController is implemented)
    combo_mode = window.findChild(QWidget, "comboMode")
    # Mode state
    state = {
        "mode": StudyMode.SYLLABLES,
        "vowel_idx": 0,
        "consonant_idx": 0,
        "anchor_consonant": "ㄱ",
    }
    CONSONANT_ORDER = _CHOESONG  # reuse existing order for now
    def _current_vowel_list():
        return VOWEL_ORDER_BASIC10  # later: include advanced based on toggle

    def _set_progress_label():
        lbl = window.findChild(QLabel, "labelProgress")
        if lbl is None:
            return
        if state["mode"] in (StudyMode.SYLLABLES, StudyMode.VOWELS):
            pos = state["vowel_idx"] + 1
            total = len(_current_vowel_list())
            lbl.setText(f"Vowel {pos}/{total}")
        else:
            pos = state["consonant_idx"] + 1
            total = len(CONSONANT_ORDER)
            lbl.setText(f"Consonant {pos}/{total}")

    def refresh_view():
        if state["mode"] == StudyMode.SYLLABLES:
            v = _current_vowel_list()[state["vowel_idx"]]
            manager.show_pair(stacked, state["anchor_consonant"], v, type_label, syll_label)
        elif state["mode"] == StudyMode.VOWELS:
            v = _current_vowel_list()[state["vowel_idx"]]
            manager.show_pair(stacked, "ㅇ", v, type_label, syll_label)  # silent placeholder ㅇ as L
        else:  # CONSONANTS
            c = CONSONANT_ORDER[state["consonant_idx"]]
            manager.show_consonant(stacked, c, type_label, syll_label)
        _set_progress_label()

    refresh_view()

    # Helper to show which page is active (by objectName if present)
    def _describe_page(i: int) -> str:
        w = stacked.widget(i)
        name = w.objectName() if (w is not None and w.objectName()) else "page#{}".format(i)
        return "index={} ({})".format(i, name)

    print("[INFO] Startup page -> {}".format(_describe_page(stacked.currentIndex())))

    # Wire the Next button to cycle through block types (wrap-around)
    btn_next = window.findChild(QPushButton, "buttonNext")
    if btn_next is None:
        print("[WARN] 'buttonNext' not found in form.ui; cycling disabled", file=sys.stderr)
    else:
        def on_next():
            if state["mode"] in (StudyMode.SYLLABLES, StudyMode.VOWELS):
                state["vowel_idx"] = (state["vowel_idx"] + 1) % len(_current_vowel_list())
            else:
                state["consonant_idx"] = (state["consonant_idx"] + 1) % len(CONSONANT_ORDER)
            refresh_view()
            print("[INFO] Next -> {}".format(_describe_page(stacked.currentIndex())))

        cast(QObject, btn_next.clicked).connect(on_next)

    # --- Wire the rest of the control strip ---
    btn_prev = window.findChild(QPushButton, "buttonPrev")
    chk_rare = window.findChild(QCheckBox, "checkIncludeRare")
    chk_adv_vowels = window.findChild(QCheckBox, "checkAdvancedVowels")
    label_progress = window.findChild(QLabel, "labelProgress")

    # Minimal state (until ProgressionController is implemented)
    include_rare = {"value": False}
    use_advanced_vowels = {"value": False}

    # Prev button -> cycle block types backwards (placeholder behavior)
    if btn_prev is not None:
        def on_prev():
            if state["mode"] in (StudyMode.SYLLABLES, StudyMode.VOWELS):
                state["vowel_idx"] = (state["vowel_idx"] - 1) % len(_current_vowel_list())
            else:
                state["consonant_idx"] = (state["consonant_idx"] - 1) % len(CONSONANT_ORDER)
            refresh_view()
            print("[INFO] Prev -> {}".format(_describe_page(stacked.currentIndex())))

        cast(QObject, btn_prev.clicked).connect(on_prev)

    # Wire Mode combobox
    def _on_mode_changed(idx: int):
        mapping = {0: StudyMode.SYLLABLES, 1: StudyMode.VOWELS, 2: StudyMode.CONSONANTS}
        state["mode"] = mapping.get(idx, StudyMode.SYLLABLES)
        # Reset indices when switching modes for a predictable start
        state["vowel_idx"] = 0
        state["consonant_idx"] = 0
        refresh_view()
    try:
        if hasattr(combo_mode, 'currentIndexChanged'):
            combo_mode.currentIndexChanged.connect(_on_mode_changed)
    except Exception:
        pass

    # Toggles
    if chk_rare is not None:
        chk_rare.toggled.connect(lambda v: include_rare.__setitem__("value", bool(v)))
    if chk_adv_vowels is not None:
        chk_adv_vowels.toggled.connect(lambda v: use_advanced_vowels.__setitem__("value", bool(v)))

    # --- Drawer toggle logic (slide open/close) ---
    def _toggle_drawer():
        if drawer_left is None:
            return
        target_open = (drawer_left.maximumHeight() == 0)
        start_h = drawer_left.maximumHeight()
        # Measure desired height using sizeHint when expanding
        end_h = drawer_left.sizeHint().height() if target_open else 0
        # Make sure it's visible before expanding
        if target_open and not drawer_left.isVisible():
            drawer_left.setVisible(True)
        anim = QPropertyAnimation(drawer_left, b"maximumHeight")
        anim.setDuration(220)
        anim.setStartValue(start_h)
        anim.setEndValue(end_h)
        anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        # Keep a reference to avoid GC during animation
        window._drawer_anim = anim

        def _on_finished():
            if end_h == 0:
                drawer_left.setVisible(False)

        anim.finished.connect(_on_finished)
        anim.start()

        # Connect menu action now that the slot exists (if not already connected)
        try:
            action_toggle = window.findChild(QAction, "actionToggleDrawer")
            if action_toggle is not None:
                try:
                    action_toggle.triggered.disconnect()
                except Exception:
                    pass
                action_toggle.triggered.connect(_toggle_drawer)
        except Exception:
            pass

    # --- Toolbar with hamburger (top, left-aligned) ---
    try:
        toolbar = window.findChild(QToolBar, "mainToolbar")
        if toolbar is None:
            toolbar = QToolBar("MainToolbar", window)
            toolbar.setObjectName("mainToolbar")
            toolbar.setMovable(False)
            toolbar.setIconSize(QSize(24, 24))
            window.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)
        action_toolbar_toggle = QAction(build_hamburger_icon(24, 2, 4), "Toggle Drawer", window)
        action_toolbar_toggle.setToolTip("Open or close the settings drawer")
        action_toolbar_toggle.triggered.connect(_toggle_drawer)
        toolbar.addAction(action_toolbar_toggle)
    except Exception as e:
        print(f"[WARN] Toolbar setup failed: {e}", file=sys.stderr)

    if button_hamburger is not None and hasattr(button_hamburger, 'clicked'):
        try:
            button_hamburger.clicked.connect(_toggle_drawer)
        except Exception:
            pass

    # Initialize UI state
    refresh_view()

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
