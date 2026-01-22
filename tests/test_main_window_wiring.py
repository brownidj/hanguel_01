import pytest
from PyQt6.QtCore import Qt

from PyQt6.QtWidgets import QLabel, QFrame, QStackedWidget, QPushButton

from app.ui.main_window import create_main_window


@pytest.mark.qt
class TestMainWindowWiring:
    def test_main_window_renders_initial_syllable_and_segments(self, qtbot):
        """
        Smoke test for end‑to‑end wiring:

        - main window builds without crashing
        - JamoBlock is attached to the stacked widget
        - Top/Middle/Bottom segment frames on the *current* page
          each receive at least one child widget
        - labelSyllableRight is updated to a composed syllable (e.g. '가')

        This intentionally mirrors the behaviour that worked in
        `_ref_main_f5c83de.py`.
        """

        window = create_main_window(expose_handles=True)
        qtbot.addWidget(window)
        window.show()

        # --- stacked widget must exist ---
        stacked = window.findChild(QStackedWidget)
        assert stacked is not None, "QStackedWidget not found in main window"

        page = stacked.currentWidget()
        assert page is not None, "No current page in stacked widget"

        # --- segment frames on the current page must have content ---
        roles = ["Top", "Middle", "Bottom"]
        for role in roles:
            frames = [
                f for f in page.findChildren(QFrame)
                if f.property("segmentRole") == role
            ]
            assert frames, f"No QFrame found with segmentRole={role}"

            frame = frames[0]
            layout = frame.layout()
            assert layout is not None, f"Frame {frame.objectName()} has no layout"
            assert layout.count() >= 1, (
                f"Frame {frame.objectName()} ({role}) has no child widgets"
            )

        # --- full syllable label must be populated ---
        syll_label = window.findChild(QLabel, "labelSyllableRight")
        assert syll_label is not None, "labelSyllableRight not found"

        text = syll_label.text().strip()
        assert text, "labelSyllableRight text is empty"
        assert len(text) == 1, f"Expected single Hangul syllable, got '{text}'"

    def test_next_prev_cycle_changes_block_type(self, qtbot):
        """Verify that Next/Prev wiring changes the JamoBlock template page.

        We deliberately avoid assuming a specific ownership model (window vs controller)
        or a single objectName for the buttons.
        """

        window = create_main_window(expose_handles=True)
        qtbot.addWidget(window)
        window.show()

        controller = getattr(window, "_controller", None)
        assert controller is not None

        jamo_block = window._jamo_block
        stacked = jamo_block.findChild(QStackedWidget, "stackedTemplates")
        assert stacked is not None

        def _resolve_button(attr_names: list[str], name_hints: list[str]) -> QPushButton | None:
            # 1) Prefer explicit controller handles if present.
            for attr in attr_names:
                btn = getattr(controller, attr, None)
                if isinstance(btn, QPushButton):
                    return btn

            # 2) Try direct lookup by common objectNames.
            for hint in name_hints:
                btn = window.findChild(QPushButton, hint)
                if isinstance(btn, QPushButton):
                    return btn

            # 3) Fallback: scan all buttons and match objectName / tooltip.
            for btn in window.findChildren(QPushButton):
                obj = (btn.objectName() or "").lower()
                tip = (btn.toolTip() or "").lower()
                if any(h in obj for h in name_hints) or any(h in tip for h in name_hints):
                    return btn

            return None

        next_btn = _resolve_button(
            attr_names=["next_button", "next_btn", "btn_next", "button_next"],
            name_hints=["next_btn", "btnNext", "btn_next", "next"],
        )
        prev_btn = _resolve_button(
            attr_names=["prev_button", "prev_btn", "btn_prev", "button_prev"],
            name_hints=["prev_btn", "btnPrev", "btn_prev", "prev"],
        )

        assert next_btn is not None, "Unable to locate Next button (controller handle or window child)"
        assert prev_btn is not None, "Unable to locate Prev button (controller handle or window child)"

        initial_index = stacked.currentIndex()

        qtbot.mouseClick(next_btn, Qt.MouseButton.LeftButton)
        assert stacked.currentIndex() != initial_index

        qtbot.mouseClick(prev_btn, Qt.MouseButton.LeftButton)
        assert stacked.currentIndex() == initial_index
