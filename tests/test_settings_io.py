import json
from pathlib import Path
import yaml
import importlib
import types
import pytest


@pytest.fixture
def main_module(monkeypatch, tmp_path: Path):
    """
    Import the app's main module in a way that redirects SETTINGS_PATH
    to a temporary file so tests never touch the real settings.yaml.
    """
    # Import the module
    main = importlib.import_module("main")

    # Point settings to a temp file
    settings_path = tmp_path / "settings.yaml"
    monkeypatch.setattr(main, "SETTINGS_PATH", str(settings_path), raising=False)

    return main


def test_save_and_load_roundtrip(main_module):
    """
    _save_settings should write a UTF-8 YAML file and _load_settings
    should reconstruct the same dictionary.
    """
    main = main_module
    payload = {
        "theme": "hanji",
        "wpm": 120,
        "repeats": 3,
        "delays": {
            "pre_first": 0,
            "between_reps": 2,
            "before_hints": 0,
            "before_extras": 1,
            "auto_advance": 0,
        },
    }

    # Save then load
    main._save_settings(payload)
    loaded = main._load_settings()

    assert isinstance(loaded, dict)
    assert loaded["theme"] == "hanji"
    assert loaded["wpm"] == 120
    assert loaded["repeats"] == 3
    assert isinstance(loaded["delays"], dict)
    assert loaded["delays"]["between_reps"] == 2


def test_nested_dictionary_integrity(main_module):
    """
    Ensure nested dicts like delays persist as dicts and keep numeric types.
    """
    main = main_module

    data = {
        "theme": "taegeuk",
        "delays": {
            "pre_first": 1,
            "between_reps": 3,
            "before_hints": 0,
            "before_extras": 2,
            "auto_advance": 0,
        },
    }

    main._save_settings(data)
    loaded = main._load_settings()

    assert loaded["theme"] == "taegeuk"
    d = loaded["delays"]
    assert isinstance(d, dict)
    assert d["pre_first"] == 1
    assert d["between_reps"] == 3
    assert d["before_extras"] == 2


def test_update_preserves_other_keys(main_module):
    """
    Simulate the app pattern: load -> update one key -> save.
    Ensure previously saved keys are preserved (because we load/merge/save).
    """
    main = main_module

    # First save with some keys
    main._save_settings({"theme": "taegeuk", "wpm": 80})

    # Emulate app: load, update a single key, save
    s = main._load_settings()
    s["repeats"] = 2
    main._save_settings(s)

    # Load again and verify all keys are present
    loaded = main._load_settings()
    assert loaded["theme"] == "taegeuk"
    assert loaded["wpm"] == 80
    assert loaded["repeats"] == 2
