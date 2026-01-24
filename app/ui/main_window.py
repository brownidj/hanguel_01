"""Main window factory.

This module owns construction and UI wiring for the application's main window.

Public API:
- create_main_window(...): builds and returns the main window without starting the
  Qt event loop, enabling UI tests to instantiate the window headlessly.

Design notes:
- We deliberately keep the *entrypoint* responsibilities (QApplication creation
  and app.exec()) out of this module.
- The wiring logic is migrated out of `main.py` incrementally. In the first step
  we delegate to a private builder function hosted in `main.py` so we can keep
  tests green while moving code in safe, mechanical slices.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import os
import sys
import inspect
from PyQt6 import uic
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
)

from app.controllers.main_window_controller import MainWindowController


@dataclass(frozen=True)
class MainWindowHandles:
    """Optional handles that tests may need.

    Keep this small and stable. Prefer storing references on the window instance
    (e.g. window._handles = MainWindowHandles(...)) so tests can discover them.
    """

    # Populate as you expose stable seams for tests. Keep Optional to avoid
    # hard coupling during refactors.
    pronounce_chip: Optional[Any] = None
    next_button: Optional[Any] = None
    prev_button: Optional[Any] = None


def create_main_window(*, expose_handles: bool = True, settings_path: str | None = None):
    """Create and return the application's main window.

    This function must NOT call app.exec(). It may assume a QApplication exists.

    Args:
        expose_handles: If True, attaches a small, stable set of UI handles for
            tests via `window._handles`.
        settings_path: Optional path to a settings.yaml to load and apply to the UI.

    Returns:
        QWidget: the loaded and wired main window.
    """

    # Explicit main window UI contract: form.ui is the main window.
    here = Path(__file__).resolve()
    project_root = here.parents[2]
    ui_path = project_root / "ui" / "form.ui"

    if not ui_path.exists():
        raise FileNotFoundError(f"Main window UI not found at expected path: {ui_path}")

    try:
        window: QWidget = uic.loadUi(str(ui_path))
    except Exception as e:
        raise RuntimeError(f"Failed to load main window UI from {ui_path}: {e}")

    controller = MainWindowController(
        window,
        settings_path=settings_path,
    )
    setattr(window, "_controller", controller)

    # Best-effort: attach commonly-used handles for tests if present.
    handles: MainWindowHandles | None = None
    # NOTE:
    # main_window.py does not discover buttons.
    # It only forwards handles explicitly exposed by the controller.
    try:
        handles = MainWindowHandles(
            pronounce_chip=getattr(window, "pronounce_chip", None) or window.findChild(QWidget, "pronounce_chip"),
            next_button=getattr(controller, "next_button", None),
            prev_button=getattr(controller, "prev_button", None),
        )
    except Exception:
        handles = None

    # Standardise on attaching handles to the window instance so tests can
    # access them even if they only receive the window.
    if expose_handles and handles is not None:
        try:
            setattr(window, "_handles", handles)
        except Exception:
            pass

    return window


def create_main_window_for_tests(settings_path: str | None = None):
    """
    Create the main window without starting the Qt event loop.

    This factory exists solely for pytest scaffolds that need a fully
    constructed window without calling app.exec().

    Returns:
        (window, handles) as returned by create_main_window
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # If the UI layer supports dependency injection for settings, prefer it.
    # Otherwise, fall back to a best-effort environment variable hint.
    kwargs: dict = {"expose_handles": True}
    if settings_path:
        kwargs["settings_path"] = settings_path
        kwargs["settings_file"] = settings_path
        kwargs["settings_yaml"] = settings_path
        try:
            os.environ["HANGUL_SETTINGS_PATH"] = settings_path
            os.environ["SETTINGS_PATH"] = settings_path
            os.environ["SETTINGS_FILE"] = settings_path
        except Exception:
            pass

    try:
        sig = inspect.signature(create_main_window)
        accepted = set(sig.parameters.keys())
        call_kwargs = {k: v for k, v in kwargs.items() if k in accepted}
    except Exception:
        call_kwargs = {"expose_handles": True}

    result = create_main_window(**call_kwargs)
    if isinstance(result, tuple) and len(result) == 2:
        window, handles = result
        return window, handles
    return result, None
