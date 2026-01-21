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
from typing import Any, Optional

from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QStackedWidget,
    QPushButton,
    QSpinBox
)


from app.ui.widgets.segments import JamoBlock



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

        print("[DEBUG] QLabel objectNames in main window:")
        for lbl in window.findChildren(QLabel):
            nm = lbl.objectName()
            if nm:
                print("   -", nm, "text=", repr(lbl.text()))
    except Exception as e:
        raise RuntimeError(f"Failed to load main window UI from {ui_path}: {e}")

    # --------------------------------------------------
    # Compose Jamo block UI into the main window
    # --------------------------------------------------
    try:
        jamo_block = JamoBlock()

        frame = window.findChild(QFrame, "frameJamoBorder")
        if frame is None:
            raise RuntimeError("frameJamoBorder not found")

        layout = frame.layout()
        if layout is None or layout.objectName() != "layoutInnerJamo":
            raise RuntimeError("layoutInnerJamo not found on frameJamoBorder")

        # Optional: avoid duplicates if this factory is called more than once
        # while layout.count():
        #     item = layout.takeAt(0)
        #     w = item.widget()
        #     if w is not None:
        #         w.setParent(None)

        layout.addWidget(jamo_block)
        # Keep a stable reference for later wiring/tests
        try:
            setattr(window, "_jamo_block", jamo_block)
        except Exception:
            pass

        # The old render pipeline expects the stacked widget from jamo.ui

        stacked = jamo_block.findChild(QStackedWidget, "stackedTemplates")
        if stacked is None:
            raise RuntimeError("stackedTemplates not found inside JamoBlock (check jamo.ui objectName)")

        # Import the existing driver (BlockManager) without reintroducing UI loading.
        # This assumes main.py does NOT execute the app loop on import (i.e. guarded by if __name__ == '__main__').
        from main import BlockManager  # keep local to avoid circular imports at module import time

        block_manager = BlockManager()

        # Labels in form.ui
        # - labelSyllableRight exists (discovered via debug print) and is where the full composed syllable should show.
        type_label: QLabel | None = None
        syll_label: QLabel | None = window.findChild(QLabel, "labelSyllableRight")
        if syll_label is not None:
            # Make it visually obvious during debugging (if it's present but not visible).
            try:
                syll_label.setStyleSheet(
                    "border: 2px solid #ff0000; background: #ffffcc; color: #000000; font-size: 48px;"
                )
                syll_label.setMinimumHeight(60)
                syll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            except Exception:
                pass

            syll_label.setText("가")
            print(
                "[DEBUG] smoke: labelSyllableRight set to", repr(syll_label.text()),
                "visible=", syll_label.isVisible(),
                "geo=", syll_label.geometry().width(), "x", syll_label.geometry().height(),
                "+", syll_label.geometry().x(), "+", syll_label.geometry().y(),
                "parent=", type(syll_label.parent()).__name__ if syll_label.parent() is not None else None,
            )
        else:
            print("[DEBUG] labelSyllableRight NOT FOUND")

        # Optional: if you later add a dedicated block-type label, wire it here.
        # type_label = window.findChild(QLabel, "labelBlockType")

        bt = block_manager.current_type()

        # Call show_pair using keyword arguments matched to its real signature.
        # This avoids positional/keyword mismatches during refactors.
        import inspect

        sig = inspect.signature(block_manager.show_pair)
        param_names = set(sig.parameters.keys())
        # drop self if present
        param_names.discard("self")

        kwargs: dict[str, Any] = {}

        # Block type parameter
        for nm in ("bt", "block_type", "ctype", "type"):
            if nm in param_names:
                kwargs[nm] = bt
                break

        # Consonant parameter
        for nm in ("consonant", "lead", "initial"):
            if nm in param_names:
                kwargs[nm] = "ㄱ"
                break

        # Vowel parameter
        if "vowel" in param_names:
            kwargs["vowel"] = "ㅏ"

        # Stacked widget parameter
        for nm in ("stacked", "stack", "stacked_widget"):
            if nm in param_names:
                kwargs[nm] = stacked
                break

        # Optional labels
        if "type_label" in param_names:
            kwargs["type_label"] = type_label
        if "syll_label" in param_names:
            kwargs["syll_label"] = syll_label

        # Sanity: ensure required args are satisfied
        missing_required: list[str] = []
        for p in sig.parameters.values():
            if p.name == "self":
                continue
            if p.default is inspect._empty and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD, p.KEYWORD_ONLY):
                if p.name not in kwargs:
                    missing_required.append(p.name)
        if missing_required:
            raise RuntimeError(
                "Cannot call BlockManager.show_pair(); missing required args: {}".format(
                    ", ".join(missing_required)
                )
            )

        print("[DEBUG] calling show_pair with keys:", sorted(kwargs.keys()))
        print("[DEBUG] show_pair signature:", sig)
        block_manager.show_pair(**kwargs)
        if syll_label is not None:
            print(
                "[DEBUG] after show_pair: labelSyllableRight =", repr(syll_label.text()),
                "visible=", syll_label.isVisible(),
                "geo=", syll_label.geometry().width(), "x", syll_label.geometry().height(),
                "+", syll_label.geometry().x(), "+", syll_label.geometry().y(),
            )

        # Wire Next/Prev to cycle block types using the existing BlockManager methods.
        next_btn = window.findChild(QPushButton, "next_btn")
        prev_btn = window.findChild(QPushButton, "prev_btn")

        if next_btn is not None:
            next_btn.clicked.connect(lambda: block_manager.next(stacked, type_label=type_label, syll_label=syll_label))
        if prev_btn is not None:
            prev_btn.clicked.connect(lambda: block_manager.prev(stacked, type_label=type_label, syll_label=syll_label))

        # Keep a stable reference so handlers/tests can access the driver
        try:
            setattr(window, "_block_manager", block_manager)
        except Exception:
            pass

    except Exception as e:
        raise RuntimeError(f"Failed to compose Jamo block UI: {e}")

    handles = MainWindowHandles()

    def _apply_persisted_settings(target: QWidget, path: str) -> None:
        """Best-effort: load settings.yaml and apply values to known spinboxes.

        Call this after UI wiring so defaults/signal handlers do not overwrite
        persisted values.
        """
        try:
            from app.services.settings_store import SettingsStore

            store = SettingsStore(settings_path=str(path))
            data = store.load() or {}

            repeats = data.get("repeats")
            delays = data.get("delays", {}) if isinstance(data.get("delays", {}), dict) else {}

            def _set(names: list[str], value: Any) -> None:
                if value is None:
                    return
                for nm in names:
                    try:
                        w = target.findChild(QSpinBox, nm)
                        if w is not None:
                            w.setValue(int(value))
                    except Exception:
                        pass

            _set(["spinRepeats"], repeats)
            _set(["spinDelayPreFirst", "spinPreFirst"], delays.get("pre_first"))
            _set(["spinDelayBetweenReps", "spinBetweenReps"], delays.get("between_reps"))
            _set(["spinDelayBeforeHints", "spinBeforeHints"], delays.get("before_hints"))
            _set(["spinDelayBeforeExtras", "spinBeforeExtras"], delays.get("before_extras"))
            _set(["spinDelayAutoAdvance", "spinAutoAdvance"], delays.get("auto_advance"))
        except Exception:
            return

    # Best-effort: attach commonly-used handles for tests if present.
    try:
        handles = MainWindowHandles(
            pronounce_chip=getattr(window, "pronounce_chip", None) or window.findChild(QWidget, "pronounce_chip"),
            next_button=getattr(window, "next_btn", None) or window.findChild(QWidget, "next_btn"),
            prev_button=getattr(window, "prev_btn", None) or window.findChild(QWidget, "prev_btn"),
        )
    except Exception:
        pass

    # Apply persisted settings late so subsequent wiring cannot overwrite values.
    if settings_path:
        _apply_persisted_settings(window, str(settings_path))

    # Standardise on attaching handles to the window instance so tests can
    # access them even if they only receive the window.
    if expose_handles:
        try:
            setattr(window, "_handles", handles)
        except Exception:
            pass

    return window
