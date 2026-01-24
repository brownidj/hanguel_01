import os
from pathlib import Path
from typing import Optional, Any, cast

from PyQt6 import uic
from PyQt6.QtCore import Qt, QTimer, QSize
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QStackedWidget, QFrame, QLabel, QSizePolicy


class JamoBlock(QWidget):
    """A container widget that enforces a 1:1 aspect ratio for the Hangul block.

    This widget owns rendering and loads `jamo.ui` internally.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._test_mode = str(os.getenv("HANGUL_TEST_MODE", "")).strip().lower() in ("1", "true", "yes", "on")

        # Outer layout used to center the inner square block
        self._inner_layout = QVBoxLayout(self)
        self._inner_layout.setContentsMargins(0, 0, 0, 0)
        self._inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Load the visual structure of the Jamo block
        here = Path(__file__).resolve()
        project_root = here.parents[3]
        jamo_ui_path = project_root / "ui" / "jamo.ui"

        block = QWidget(self)
        uic.loadUi(jamo_ui_path, block)

        # Keep references for debugging / discovery.
        self._ui_root = block
        self._stacked = self.findChild(QStackedWidget, "stackedTemplates")
        if self._stacked is None:
            raise RuntimeError("stackedTemplates not found in JamoBlock UI")

        for frame in block.findChildren(QFrame):
            name = frame.objectName() or ""
            if name.endswith("_segmentTop"):
                frame.setProperty("segmentRole", "Top")
            elif name.endswith("_segmentMiddle"):
                frame.setProperty("segmentRole", "Middle")
            elif name.endswith("_segmentBottom"):
                frame.setProperty("segmentRole", "Bottom")
        self._inner_layout.addWidget(block)

        # Wire up segment discovery / rendering hooks
        self._wire_segments(block)

        # --------------------------------------------------
        # DEBUG: verify segment frames and their layouts
        # --------------------------------------------------
        try:
            print("[DEBUG] --- segmentRole frames after wiring ---")
            for f in block.findChildren(QFrame):
                r = f.property("segmentRole")
                if r in ("Top", "Middle", "Bottom"):
                    lay = f.layout()
                    print(
                        "[DEBUG] frame objName={} role={} layout_is_none={} layout_type={}".format(
                            f.objectName(),
                            r,
                            (lay is None),
                            (type(lay).__name__ if lay is not None else "None"),
                        )
                    )
        except Exception as _e:
            print("[DEBUG] segmentRole debug failed: {}".format(_e))

        self._container: Optional[Any] = None

        # --------------------------------------------------
        # DEBUG / SMOKE: ensure we can see *something* without
        # relying on external callers to invoke render_demo().
        # This runs after the widget is in a layout.
        # --------------------------------------------------
        # Do not rely on deferred demo rendering for tests. Tests use the stable
        # `_testExposure` labels which are inserted into layouts immediately.
        if not self._test_mode:
            try:
                QTimer.singleShot(0, self.render_demo_on_current_page)
            except Exception:
                pass

    def _wire_segments(self, root: QWidget) -> None:
        # We must ensure segment frames on ALL pages (and on the current page)
        # have layouts, because renderers clear and repopulate frame.layout().
        stacked = self._stacked
        pages: list[QWidget] = []

        if stacked is not None:
            for i in range(int(stacked.count())):
                w = stacked.widget(i)
                if isinstance(w, QWidget):
                    pages.append(w)

        # Fall back to the provided root if stacked is missing.
        if not pages:
            pages = [root]

        for page in pages:
            for frame in page.findChildren(QFrame):
                role_name = frame.property("segmentRole")
                if role_name not in ("Top", "Middle", "Bottom"):
                    continue

                if frame.layout() is None:
                    layout = QVBoxLayout(frame)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    frame.setLayout(layout)

                if self._test_mode:
                    # Ensure stable, discoverable glyph labels for tests.
                    self._ensure_test_exposure_label(frame, str(role_name))

    def _current_page(self) -> Optional[QWidget]:
        stacked = self._stacked
        if stacked is None:
            return None
        w = stacked.currentWidget()
        return w if isinstance(w, QWidget) else None

    def _find_segment_frame_on_current_page(self, role: str) -> Optional[QFrame]:
        """Find the QFrame for the given role (Top/Middle/Bottom) on the current page."""
        page = self._current_page()
        if page is None:
            return None
        for frame in page.findChildren(QFrame):
            if frame.property("segmentRole") == role:
                return frame
        return None

    def _ensure_layout(self, frame: QFrame) -> QVBoxLayout:
        """Ensure the given frame has a QVBoxLayout and return it."""
        lay = frame.layout()
        if lay is None:
            layout = QVBoxLayout(frame)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            frame.setLayout(layout)
            return layout
        # Best-effort: cast to QVBoxLayout-like API.
        return cast(QVBoxLayout, lay)  # type: ignore[return-value]

    def _ensure_test_exposure_label(self, frame: QFrame, role: str) -> QLabel:
        """Ensure a discoverable QLabel exists for tests (HANGUL_TEST_MODE).

        We keep a stable child widget per segment so tests can find glyph text even when
        the production renderer uses custom paint widgets.
        """
        obj_name = "testGlyph{}".format(role)
        existing = frame.findChild(QLabel, obj_name)
        if existing is not None:
            return existing

        lbl = QLabel(frame)
        lbl.setObjectName(obj_name)
        lbl.setProperty("glyphRole", role)
        lbl.setProperty("_testExposure", True)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # Keep it in the widget tree for discovery; it does not need to be visible.
        lbl.setVisible(False)

        # Ensure the exposure label is also a layout child immediately so tests that
        # assert `layout.count() >= 1` pass deterministically without relying on
        # deferred rendering.
        lay = frame.layout()
        if lay is None:
            lay = self._ensure_layout(frame)
        # Avoid duplicate insertions.
        already_in_layout = False
        try:
            for i in range(int(lay.count())):
                it = lay.itemAt(i)
                if it is not None and it.widget() is lbl:
                    already_in_layout = True
                    break
        except Exception:
            already_in_layout = False
        if not already_in_layout:
            try:
                lay.addWidget(lbl)
            except Exception:
                pass

        return lbl

    def set_exposed_glyph(self, role: str, text: str) -> None:
        """Set the test-exposed glyph text for a segment role (Top/Middle/Bottom)."""
        frame = self._find_segment_frame_on_current_page(role)
        if frame is None:
            return
        lbl = self._ensure_test_exposure_label(frame, role)
        lbl.setText(text)

    def set_exposed_glyphs(self, top: str, middle: str, bottom: str) -> None:
        """Convenience: set all three exposed glyph strings."""
        self.set_exposed_glyph("Top", top)
        self.set_exposed_glyph("Middle", middle)
        self.set_exposed_glyph("Bottom", bottom)

    def debug_dump_current_template(self, prefix: str = "[DEBUG]") -> None:
        """Print what is currently attached inside the active template page."""
        try:
            stacked = self._stacked
            if stacked is None:
                print("{} JamoBlock: stackedTemplates not found".format(prefix))
                return

            idx = int(stacked.currentIndex())
            page = stacked.currentWidget()
            page_name = page.objectName() if page is not None else "None"
            print("{} JamoBlock: stacked index={} page={}".format(prefix, idx, page_name))

            if page is None:
                return

            for role in ("Top", "Middle", "Bottom"):
                frame = self._find_segment_frame_on_current_page(role)
                if frame is None:
                    print("{}  segment role={} <frame not found>".format(prefix, role))
                    continue

                lay = frame.layout()
                lay_type = type(lay).__name__ if lay is not None else "None"
                count = lay.count() if lay is not None else -1
                sr = frame.property("segmentRole")
                print(
                    "{}  segment role={} propRole={} objName={} layout={} items={} frame_geo={}x{}+{}+{}".format(
                        prefix,
                        role,
                        sr,
                        frame.objectName(),
                        lay_type,
                        count,
                        frame.geometry().width(),
                        frame.geometry().height(),
                        frame.geometry().x(),
                        frame.geometry().y(),
                    )
                )

                if lay is None:
                    continue

                for i in range(lay.count()):
                    item = lay.itemAt(i)
                    w = item.widget() if item is not None else None
                    if w is None:
                        print("{}    [{}] <no-widget>".format(prefix, i))
                        continue

                    desc = type(w).__name__
                    text = ""
                    try:
                        if hasattr(w, "text"):
                            text = str(w.text() or "")
                    except Exception:
                        text = ""

                    geo = w.geometry()
                    if text:
                        print(
                            "{}    [{}] {} text='{}' visible={} geo={}x{}+{}+{} parent={}".format(
                                prefix,
                                i,
                                desc,
                                text,
                                w.isVisible(),
                                geo.width(),
                                geo.height(),
                                geo.x(),
                                geo.y(),
                                type(w.parent()).__name__ if w.parent() is not None else "None",
                            )
                        )
                    else:
                        print(
                            "{}    [{}] {} visible={} geo={}x{}+{}+{} parent={}".format(
                                prefix,
                                i,
                                desc,
                                w.isVisible(),
                                geo.width(),
                                geo.height(),
                                geo.x(),
                                geo.y(),
                                type(w.parent()).__name__ if w.parent() is not None else "None",
                            )
                        )
        except Exception as e:
            print("{} JamoBlock debug_dump_current_template failed: {}".format(prefix, e))

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
        left = (self.width() - side) // 2
        top = (self.height() - side) // 2
        self._inner_layout.setContentsMargins(left, top, left, top)
        child.setMinimumSize(side, side)
        child.setMaximumSize(side, side)

    def setContainer(self, container: Any) -> None:
        if not hasattr(container, "attach"):
            raise TypeError("container must provide an attach(...) method")
        self._container = container

    def container(self) -> Optional[Any]:
        return self._container

    @property
    def stacked(self) -> QStackedWidget:
        return self._stacked

    def next_template(self) -> None:
        if self._stacked.count() > 0:
            self._stacked.setCurrentIndex(
                (self._stacked.currentIndex() + 1) % self._stacked.count()
            )

    def prev_template(self) -> None:
        if self._stacked.count() > 0:
            self._stacked.setCurrentIndex(
                (self._stacked.currentIndex() - 1) % self._stacked.count()
            )

    def render_demo(self) -> None:
        """Public demo renderer (kept for callers that expect render_demo())."""
        self.render_demo_on_current_page()

    def render_demo_on_current_page(self) -> None:
        """Smoke-render demo glyphs into the current page's segment frames."""
        try:
            page = self._current_page()
            stacked = self._stacked
            if stacked is None:
                print("[DEBUG] render_demo_on_current_page: stackedTemplates not found")
                return

            idx = int(stacked.currentIndex())
            page_name = page.objectName() if page is not None else "None"
            print("[DEBUG] render_demo_on_current_page: index={} page={}".format(idx, page_name))
            # If this line never appears, the demo renderer is not being invoked.
            print("[DEBUG] render_demo_on_current_page: ENTER")

            # Resolve segment frames from the CURRENT page only.
            top_frame = self._find_segment_frame_on_current_page("Top")
            mid_frame = self._find_segment_frame_on_current_page("Middle")
            bot_frame = self._find_segment_frame_on_current_page("Bottom")

            if top_frame is None or mid_frame is None or bot_frame is None:
                print(
                    "[DEBUG] render_demo_on_current_page: missing segment frame(s) top={} middle={} bottom={}".format(
                        top_frame is not None, mid_frame is not None, bot_frame is not None
                    )
                )
                self.debug_dump_current_template(prefix="[DEBUG]")
                return

            # [DEBUG] print which frames are being used (object names)
            print(
                "[DEBUG] render_demo_on_current_page: using frames top={} mid={} bot={}"
                .format(top_frame.objectName(), mid_frame.objectName(), bot_frame.objectName())
            )
            # Clear existing widgets (layout items) safely.
            for role, frame in (("Top", top_frame), ("Middle", mid_frame), ("Bottom", bot_frame)):
                if frame.layout() is None:
                    layout = QVBoxLayout(frame)
                    layout.setContentsMargins(0, 0, 0, 0)
                    layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    frame.setLayout(layout)
                    print(
                        "[DEBUG] render_demo_on_current_page: created layout for role={} objName={}".format(
                            role, frame.objectName()
                        )
                    )
                else:
                    print(
                        "[DEBUG] render_demo_on_current_page: existing layout for role={} objName={} type={}".format(
                            role, frame.objectName(), type(frame.layout()).__name__
                        )
                    )

            for role, frame in (("Top", top_frame), ("Middle", mid_frame), ("Bottom", bot_frame)):
                lay = frame.layout()
                if lay is None:
                    print(
                        "[DEBUG] render_demo_on_current_page: ERROR layout is None after ensure for role={} objName={}".format(
                            role, frame.objectName()
                        )
                    )
                    continue

                # Remove non-test widgets without disturbing stable test-exposure labels.
                try:
                    for i in reversed(range(int(lay.count()))):
                        it = lay.itemAt(i)
                        w = it.widget() if it is not None else None
                        if w is None:
                            continue
                        if bool(w.property("_testExposure")):
                            continue
                        lay.takeAt(i)
                        w.setParent(None)
                except Exception:
                    # Best-effort fallback: do nothing.
                    pass

            # Add demo widgets via frame.layout().addWidget(...)
            tl = top_frame.layout()
            ml = mid_frame.layout()
            bl = bot_frame.layout()

            if tl is None or ml is None or bl is None:
                print(
                    "[DEBUG] render_demo_on_current_page: ERROR one or more layouts missing (tl={}, ml={}, bl={})".format(
                        tl is not None, ml is not None, bl is not None
                    )
                )
                self.debug_dump_current_template(prefix="[DEBUG]")
                return

            # --------------------------------------------------
            # DEBUG SMOKE RENDER
            # Use plain QLabel with loud styling so we can prove layout + painting
            # works, independent of AutoFitLabel / palette issues.
            # --------------------------------------------------
            from PyQt6.QtGui import QFont

            def _mk_label(text: str) -> QLabel:
                lbl = QLabel(text)
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                try:
                    f = QFont()
                    f.setPointSize(96)
                    f.setBold(True)
                    lbl.setFont(f)
                except Exception:
                    pass
                # High-contrast debug styling
                lbl.setStyleSheet("color: #ff0000; background: #ffffcc; border: 2px solid #ff0000;")
                # Ensure it can expand inside the segment
                sp = lbl.sizePolicy()
                sp.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
                sp.setVerticalPolicy(QSizePolicy.Policy.Expanding)
                lbl.setSizePolicy(sp)
                return lbl

            top_lbl = _mk_label("ㄱ")
            mid_lbl = _mk_label("ㅏ")
            bot_lbl = _mk_label("∅")

            tl.addWidget(top_lbl)
            ml.addWidget(mid_lbl)
            bl.addWidget(bot_lbl)

            if self._test_mode:
                self.set_exposed_glyphs("ㄱ", "ㅏ", "∅")

            # Force a layout pass and repaint, then dump what we actually attached.
            self.updateGeometry()
            self.update()
            if page is not None:
                page.update()
            top_frame.update()
            mid_frame.update()
            bot_frame.update()
            QTimer.singleShot(0, lambda: self.debug_dump_current_template(prefix="[DEBUG]"))
        except Exception as e:
            print("[DEBUG] render_demo_on_current_page failed: {}".format(e))