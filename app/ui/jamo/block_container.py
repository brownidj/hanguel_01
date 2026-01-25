from __future__ import annotations

from typing import Optional, List

from PyQt6.QtCore import QSize, Qt
# --- PyQt6 multimedia imports (for QSoundEffect) ---
from PyQt6.QtWidgets import (
    QWidget,
    QStackedWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
)

from app.domain.enums import (
    BlockType,
    SegmentRole,
    ConsonantPosition,
)
from app.domain.hangul_compose import compose_cv
from app.domain.syllables import select_syllable_for_block
from app.ui.utils.layout import (
    _deep_clear_container,
    _ensure_empty_placeholder,
    _enforce_equal_segment_heights,
)
from app.ui.widgets.labels import _mk_title_label
from app.ui.widgets.segments import SegmentView, ConsonantView, VowelView

# --- Segment label text (tooltips and titles) ---
# These were previously defined in main.py; BlockContainer needs them for UI tooltips.
SEG_TITLES = {
    "L": "Leading consonant",
    "V": "Vowel",
    "T": "Trailing consonant",
}

SEG_TIPS = {
    "L": "Leading consonant (initial).",
    "V": "Medial vowel.",
    "T": "Trailing consonant (final).",
}


class BlockContainer:
    """Holds one block type (A–D) and renders three segment frames.

    Invariant:
      - Must be constructed with a non-null BlockType.
      - Owns exactly three segments: Top, Middle, Bottom (in that order).
    """

    def __init__(self, block_type: BlockType):
        if block_type is None or not isinstance(block_type, BlockType):
            raise ValueError("BlockContainer requires a valid BlockType")
        self._type: BlockType = block_type

    @property
    def type(self) -> BlockType:
        return self._type

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

        def _coerce_role(r):
            """Normalise role values to SegmentRole.

            Some widgets may return role as a string (e.g. 'Top'), while others
            return the SegmentRole enum. We normalise to SegmentRole so downstream
            code is stable.
            """
            if isinstance(r, SegmentRole):
                return r
            if isinstance(r, str):
                mapping = {
                    "Top": SegmentRole.Top,
                    "Middle": SegmentRole.Middle,
                    "Bottom": SegmentRole.Bottom,
                }
                return mapping.get(r)
            return None

        for v in views:
            r = _coerce_role(v.role())
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

        # Hard fail if any segment is missing so the error is explicit
        if top_w is None or mid_w is None or bot_w is None:
            raise RuntimeError(
                "Unable to locate segment placeholders on page '{}'. "
                "Found roles: {}".format(
                    page.objectName(),
                    ", ".join(r.name for r in sorted(role_to_widget.keys(), key=lambda x: x.value))
                )
            )

        # Clear and place presenters per type
        if top_w is not None:
            _deep_clear_container(top_w)
        if mid_w is not None:
            _deep_clear_container(mid_w)
        if bot_w is not None:
            _deep_clear_container(bot_w)

        def _segment_layout(w: Optional[QWidget], title: str | None, tooltip: Optional[str] = None) -> Optional[QVBoxLayout]:
            if w is None:
                return None
            layout = w.layout()
            if layout is None:
                layout = QVBoxLayout(w)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if title:
                t = _mk_title_label(title)
                if tooltip:
                    try:
                        t.setToolTip(tooltip)
                    except Exception:
                        pass
                layout.addWidget(t)
            return layout  # type: ignore[return-value]

        # TYPE A
        if self._type == BlockType.A_RightBranch:
            # Top: L+V side by side
            if top_w is not None:
                _segment_layout(top_w, None)
                cons = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                cons.setToolTip("Leading")
                vow = VowelView(top_w, vowel_char)
                vow.setToolTip("Vowel")
                _add_row(top_w, [cons, vow])
            # Middle: empty (by design)
            # Bottom: empty (no T)
            if bot_w is not None:
                _segment_layout(bot_w, SEG_TITLES["T"], SEG_TIPS["T"])

        # TYPE B
        elif self._type == BlockType.B_TopBranch:
            # Top: V; Middle: L; Bottom: T
            if top_w is not None:
                _segment_layout(top_w, None)
                v_top = VowelView(top_w, vowel_char)
                v_top.setToolTip("Vowel")
                top_layout = top_w.layout()
                if top_layout is None:
                    top_layout = QVBoxLayout(top_w)
                top_layout.addWidget(v_top)

            if mid_w is not None:
                _segment_layout(mid_w, None)
                c_mid = ConsonantView(mid_w, cons_char, ConsonantPosition.Initial)
                c_mid.setToolTip("Leading")
                mid_layout = mid_w.layout()
                if mid_layout is None:
                    mid_layout = QVBoxLayout(mid_w)
                mid_layout.addWidget(c_mid)

            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                _segment_layout(bot_w, SEG_TITLES["T"], SEG_TIPS["T"])

        elif self._type == BlockType.C_BottomBranch:
            # Top: L; Middle: V; Bottom: T
            if top_w is not None:
                _segment_layout(top_w, None)
                c_top = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                c_top.setToolTip("Leading")
                top_layout = top_w.layout()
                if top_layout is None:
                    top_layout = QVBoxLayout(top_w)
                top_layout.addWidget(c_top)
            if mid_w is not None:
                _segment_layout(mid_w, None)
                v_mid = VowelView(mid_w, vowel_char)
                v_mid.setToolTip("Vowel")
                mid_layout = mid_w.layout()
                if mid_layout is None:
                    mid_layout = QVBoxLayout(mid_w)
                mid_layout.addWidget(v_mid)
            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                _segment_layout(bot_w, SEG_TITLES["T"], SEG_TIPS["T"])

        elif self._type == BlockType.D_Horizontal:
            # Top: L; Middle: V; Bottom: T
            if top_w is not None:
                _segment_layout(top_w, None)
                c_top = ConsonantView(top_w, cons_char, ConsonantPosition.Initial)
                c_top.setToolTip("Leading")
                top_layout = top_w.layout()
                if top_layout is None:
                    top_layout = QVBoxLayout(top_w)
                top_layout.addWidget(c_top)
            if mid_w is not None:
                _segment_layout(mid_w, None)
                v_mid = VowelView(mid_w, vowel_char)
                v_mid.setToolTip("Vowel")
                mid_layout = mid_w.layout()
                if mid_layout is None:
                    mid_layout = QVBoxLayout(mid_w)
                mid_layout.addWidget(v_mid)
            # Bottom: T subtitle only (no glyph)
            if bot_w is not None:
                _segment_layout(bot_w, SEG_TITLES["T"], SEG_TIPS["T"])

        def _ensure_placeholder_if_empty(w: Optional[QWidget]) -> None:
            if w is None:
                return
            layout = w.layout()
            if layout is None or layout.count() == 0:
                ph = _ensure_empty_placeholder(w)
                try:
                    ph.setText("")
                    ph.setVisible(False)
                except Exception:
                    pass

        _ensure_placeholder_if_empty(top_w)
        _ensure_placeholder_if_empty(mid_w)
        _ensure_placeholder_if_empty(bot_w)
        _enforce_equal_segment_heights([w for w in (top_w, mid_w, bot_w) if w is not None])
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
            if isinstance(r, SegmentRole):
                role_to_widget[r] = v
            elif isinstance(r, str):
                mapping = {"Top": SegmentRole.Top, "Middle": SegmentRole.Middle, "Bottom": SegmentRole.Bottom}
                rr = mapping.get(r)
                if rr is not None:
                    role_to_widget[rr] = v
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
        _deep_clear_container(top_w)
        _deep_clear_container(mid_w)  # ensure any prior vowel is gone
        _deep_clear_container(bot_w)

        def _segment_layout(w: Optional[QWidget], title: str | None, tooltip: Optional[str] = None) -> Optional[QVBoxLayout]:
            if w is None:
                return None
            layout = w.layout()
            if layout is None:
                layout = QVBoxLayout(w)
            layout.setContentsMargins(4, 4, 4, 4)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if title:
                t = _mk_title_label(title)
                if tooltip:
                    try:
                        t.setToolTip(tooltip)
                    except Exception:
                        pass
                layout.addWidget(t)
            return layout  # type: ignore[return-value]

        # Add title + consonant glyph in top
        top_lay = _segment_layout(top_w, None)
        if top_lay is not None:
            cons = ConsonantView(top_w, consonant, ConsonantPosition.Initial)
            cons.setToolTip("Leading")  # Leading consonant
            top_lay.addWidget(cons, 1)

        # Middle: V title only (no glyph)
        _segment_layout(mid_w, None)

        # Bottom: T title only (no glyph)
        _segment_layout(bot_w, SEG_TITLES["T"], SEG_TIPS["T"])
        def _ensure_placeholder_if_empty(w: Optional[QWidget]) -> None:
            if w is None:
                return
            layout = w.layout()
            if layout is None or layout.count() == 0:
                ph = _ensure_empty_placeholder(w)
                try:
                    ph.setText("")
                    ph.setVisible(False)
                except Exception:
                    pass

        _ensure_placeholder_if_empty(top_w)
        _ensure_placeholder_if_empty(mid_w)
        _ensure_placeholder_if_empty(bot_w)
        _enforce_equal_segment_heights([w for w in (top_w, mid_w, bot_w) if w is not None])
        page.updateGeometry()
        page.update()
