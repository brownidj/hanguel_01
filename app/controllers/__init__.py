"""
Controller package exports.

This file exists to make controller modules discoverable to static analysis
(PyCharm inspections) and to provide a stable import surface.
"""

# Canonical controllers
from .main_window_controller import MainWindowController  # noqa: F401
from .pronunciation_controller import PronunciationController  # noqa: F401

# Legacy compatibility:
# Some older code expected `app.controllers.block_manager` to be a module.
# That functionality now lives in main_window_controller.
from . import main_window_controller as block_manager  # noqa: F401

__all__ = [
    "MainWindowController",
    "PronunciationController",
    "block_manager",
]
