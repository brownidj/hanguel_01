# tests/conftest.py
import os
import importlib
import pytest
from typing import Optional
from PyQt6.QtWidgets import QApplication

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