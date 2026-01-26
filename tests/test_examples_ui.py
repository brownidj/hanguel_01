from __future__ import annotations

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QComboBox, QPushButton

from app.ui.main_window import create_main_window
import app.controllers.examples_ui_controller as examples_ui_controller


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


@pytest.mark.qt
def test_examples_hear_plays_example_audio(monkeypatch, qtbot):
    window = create_main_window(expose_handles=True)
    qtbot.addWidget(window)
    window.show()

    combo: QComboBox | None = window.findChild(QComboBox, "comboMode")
    assert combo is not None

    label_hangul: QLabel | None = window.findChild(QLabel, "labelExampleHangulPlain")
    assert label_hangul is not None

    btn_hear: QPushButton | None = window.findChild(QPushButton, "btnExampleHear")
    assert btn_hear is not None

    combo.setCurrentText("Vowels")
    qtbot.waitUntil(lambda: label_hangul.text() != "", timeout=1000)

    called: dict[str, str] = {}

    def _fake_play(path):
        called["path"] = str(path)

    monkeypatch.setattr(examples_ui_controller, "play_wav", _fake_play)

    qtbot.mouseClick(btn_hear, Qt.MouseButton.LeftButton)
    qtbot.waitUntil(lambda: "path" in called, timeout=1000)

    expected = label_hangul.text().strip()
    assert expected, "example hangul is empty"
    assert expected in called["path"]
    assert called["path"].endswith(".wav")
