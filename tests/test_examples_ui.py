from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QComboBox

from app.ui.main_window import create_main_window


@pytest.mark.qt
def test_examples_panel_updates_on_mode_change(qtbot):
    window = create_main_window(expose_handles=True)
    qtbot.addWidget(window)
    window.show()

    combo: QComboBox | None = window.findChild(QComboBox, "comboMode")
    assert combo is not None

    label_hangul: QLabel | None = window.findChild(QLabel, "labelExampleHangulPlain")
    assert label_hangul is not None

    combo.setCurrentText("Vowels")
    qtbot.waitUntil(lambda: label_hangul.text() != "", timeout=1000)
    assert label_hangul.text().startswith("아")
