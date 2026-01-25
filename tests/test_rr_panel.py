from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QPushButton

from app.domain.romanization_rr import romanize_cv
from app.ui.main_window import create_main_window


@pytest.mark.qt
def test_rr_panel_updates_with_navigation(qtbot):
    window = create_main_window(expose_handles=True)
    qtbot.addWidget(window)
    window.show()

    controller = getattr(window, "_controller", None)
    assert controller is not None

    label_rr: QLabel | None = window.findChild(QLabel, "labelRRValue")
    assert label_rr is not None

    next_btn: QPushButton | None = window.findChild(QPushButton, "buttonNext")
    assert next_btn is not None

    consonant, vowel = controller._nav.current_pair()
    expected = romanize_cv(consonant, vowel).rr
    assert label_rr.text() == expected

    qtbot.mouseClick(next_btn, Qt.MouseButton.LeftButton)
    consonant2, vowel2 = controller._nav.current_pair()
    expected2 = romanize_cv(consonant2, vowel2).rr

    qtbot.waitUntil(lambda: label_rr.text() == expected2, timeout=1000)
