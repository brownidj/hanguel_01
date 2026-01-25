from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QComboBox, QRadioButton

from app.services.settings_store import SettingsStore
from app.ui.main_window import create_main_window_for_tests


def test_settings_store_persists_mode_and_rr_cues(tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.yaml"
    store = SettingsStore(settings_path=str(settings_path))

    store.set_mode("Consonants")
    store.set_rr_cues(False)

    assert store.get_mode() == "Consonants"
    assert store.get_rr_cues() is False

    data = store.load()
    assert data.get("mode") == "Consonants"
    assert data.get("rr_show_cues") is False


def test_mode_and_rr_cues_restore_from_settings_qt(qtbot, tmp_path: Path) -> None:
    settings_path = tmp_path / "settings.yaml"

    win, _handles = create_main_window_for_tests(settings_path=str(settings_path))
    qtbot.addWidget(win)

    combo = win.findChild(QComboBox, "comboMode")
    radio = win.findChild(QRadioButton, "radioRRCues")
    assert combo is not None
    assert radio is not None

    combo.setCurrentText("Consonants")
    radio.setChecked(False)

    store = SettingsStore(settings_path=str(settings_path))
    qtbot.waitUntil(lambda: store.get_mode() == "Consonants", timeout=1000)
    qtbot.waitUntil(lambda: store.get_rr_cues() is False, timeout=1000)

    win2, _handles2 = create_main_window_for_tests(settings_path=str(settings_path))
    qtbot.addWidget(win2)

    combo2 = win2.findChild(QComboBox, "comboMode")
    radio2 = win2.findChild(QRadioButton, "radioRRCues")
    assert combo2 is not None
    assert radio2 is not None
    assert combo2.currentText() == "Consonants"
    assert radio2.isChecked() is False
