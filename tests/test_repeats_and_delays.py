"""
Scaffold tests for the Repeats + Delays wiring.

This suite is designed to evolve:
- It will PASS core settings tests immediately.
- UI-driven tests are conditionally skipped until the app exposes
  convenient factory/helpers for creating the main window without
  entering the Qt event loop.

Recommended next step (to enable the UI tests below):
- Expose a factory in main.py, e.g. `create_main_window()` that returns
  the loaded QMainWindow (without calling app.exec()) and wires widgets.
"""

from pathlib import Path
import importlib
import pytest
import yaml


@pytest.fixture
def main_module(monkeypatch, tmp_path: Path):
    """
    Import the app's main module with SETTINGS_PATH redirected into a temp area.
    """
    main = importlib.import_module("main")
    monkeypatch.setattr(main, "SETTINGS_PATH", str(tmp_path / "settings.yaml"), raising=False)
    return main


# ------------------------------
# Settings-level smoke tests
# ------------------------------

def test_repeats_persist_and_load(main_module):
    main = main_module
    # Save repeats and delays to settings.yaml
    payload = {
        "repeats": 4,
        "delays": {
            "pre_first": 1,
            "between_reps": 2,
            "before_hints": 0,
            "before_extras": 1,
            "auto_advance": 0,
        },
    }
    main._save_settings(payload)
    loaded = main._load_settings()
    assert loaded.get("repeats") == 4
    assert isinstance(loaded.get("delays"), dict)
    assert loaded["delays"]["between_reps"] == 2


def test_settings_file_is_utf8(main_module, tmp_path: Path):
    main = main_module
    # Include Hangul to ensure UTF-8 integrity
    payload = {"theme": "taegeuk", "last_glyph": "가", "repeats": 2}
    main._save_settings(payload)
    with open(main.SETTINGS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    assert data["last_glyph"] == "가"


# ------------------------------
# UI-level scaffolds (conditional)
# ------------------------------

@pytest.mark.skip(reason="Enable when main.py exposes create_main_window() without starting app loop.")
def test_spinboxes_restore_from_settings_qt(qtbot, monkeypatch, tmp_path: Path):
    """
    Intended UI test:
    - Save settings with repeats=3 and specific delays
    - Build main window via factory (no exec loop)
    - Assert spinboxes show saved values
    """
    import main as m
    monkeypatch.setattr(m, "SETTINGS_PATH", str(tmp_path / "settings.yaml"), raising=False)

    m._save_settings({
        "repeats": 3,
        "delays": {
            "pre_first": 2,
            "between_reps": 1,
            "before_hints": 0,
            "before_extras": 1,
            "auto_advance": 0,
        }
    })

    # Factory should return a fully wired QMainWindow, not start app.exec()
    win = m.create_main_window()  # <-- Provide this in main.py to enable this test
    qtbot.addWidget(win)

    spin_repeats = win.findChild(m.QSpinBox, "spinRepeats")
    assert spin_repeats is not None
    assert int(spin_repeats.value()) == 3

    spin_between = win.findChild(m.QSpinBox, "spinDelayBetweenReps")
    assert spin_between is not None
    assert int(spin_between.value()) == 1


@pytest.mark.skip(reason="Enable when Play/Next/Prev handlers are callable without app.exec().")
def test_orchestrator_uses_current_values(monkeypatch, qtbot, tmp_path: Path):
    """
    Intended integration test:
    - Build window, set spinRepeats=2 and known delays
    - Monkeypatch PlaybackOrchestrator.start to capture args
    - Simulate Play and assert repeat_count==2 and delays match
    """
    import main as m
    monkeypatch.setattr(m, "SETTINGS_PATH", str(tmp_path / "settings.yaml"), raising=False)

    # Build window with factory (to be provided by app)
    win = m.create_main_window()
    qtbot.addWidget(win)

    # Locate controls
    spin_repeats = win.findChild(m.QSpinBox, "spinRepeats")
    spin_between = win.findChild(m.QSpinBox, "spinDelayBetweenReps")
    chip_play = win.findChild(m.QPushButton, "chipPronounce")

    assert spin_repeats and spin_between and chip_play

    # Set values
    spin_repeats.setValue(2)
    spin_between.setValue(1)

    captured = {}
    def fake_start(*, glyph, repeat_count, delays, auto_mode):
        captured.update(dict(glyph=glyph, repeat_count=repeat_count, delays=delays, auto_mode=auto_mode))

    monkeypatch.setattr(m.PlaybackOrchestrator, "start", lambda self, **kw: fake_start(**kw), raising=True)

    # Simulate Play
    chip_play.click()

    assert captured.get("repeat_count") == 2
    assert getattr(captured.get("delays"), "between_reps_ms", None) == 1000