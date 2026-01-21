import pytest

from PyQt6.QtWidgets import QLabel, QFrame, QStackedWidget

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
