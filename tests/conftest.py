# tests/conftest.py
import importlib
import os
import sys
from pathlib import Path
from typing import Optional

import pytest
from PyQt6.QtWidgets import QApplication

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    # Ensure local imports like "app" resolve when pytest is run via a venv entrypoint.
    sys.path.insert(0, str(PROJECT_ROOT))

from app.services.settings_store import SettingsStore

# noinspection PyDuplicatedCode


def _class_name(w) -> str:
    try:
        return w.metaObject().className()
    except Exception:
        return w.__class__.__name__


def _extract_glyph_text(w) -> Optional[str]:
    for attr in ("char", "glyph", "text"):
        try:
            val = getattr(w, attr, None)
            if callable(val):
                val = val()
            if isinstance(val, str) and val:
                return val
        except Exception:
            pass
    try:
        val = w.property("char")
        if isinstance(val, str) and val:
            return val
    except Exception:
        pass
    try:
        val = w.accessibleName()
        if isinstance(val, str) and val:
            return val
    except Exception:
        pass
    return None


@pytest.fixture(scope="module")
def main_module():
    # Let tests request a “test mode” so the app exposes objectNames/roles
    os.environ.setdefault("HANGUL_TEST_MODE", "1")
    return importlib.import_module("main")


@pytest.fixture
def window(main_module, qtbot):
    win = main_module.create_main_window()
    if hasattr(main_module, "initialize_jamo_block"):
        try:
            main_module.initialize_jamo_block(win)
        except Exception:
            pass
    # Render a known Type-A example
    try:
        if hasattr(main_module, "show_pair"):
            main_module.show_pair("ㄱ", "ㅏ")
        elif hasattr(main_module, "select_syllable_for_block"):
            main_module.select_syllable_for_block("가")
    except Exception:
        pass
    qtbot.addWidget(win)
    try:
        win.show()
        qtbot.waitExposed(win, timeout=1000)
    except Exception:
        pass
    try:
        QApplication.processEvents()
    except Exception:
        pass
    return win


@pytest.fixture
def settings_store(tmp_path):
    """
    A SettingsStore pointing at a temp settings.yaml so tests never touch the real config.
    """
    settings_path = tmp_path / "settings.yaml"
    settings_path.write_text("")  # ensure file exists
    return SettingsStore(settings_path=str(settings_path))
