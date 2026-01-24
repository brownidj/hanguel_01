from __future__ import annotations

import logging
from typing import Any, cast, TypeVar

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QLabel,
    QFrame,
    QLayout,
    QPushButton,
    QSpinBox,
    QStackedWidget,
    QWidget,
    QComboBox,
)

# from app.domain.hangul_compose import compose_cv
from app.controllers.block_manager import BlockManager
from app.controllers.bottom_controls import BottomControls
from app.controllers.mode_controller import ModeController
from app.controllers.study_item_repository import StudyItemRepository
from app.controllers.syllable_navigation import SyllableNavigation
from app.controllers.template_navigator import TemplateNavigator
from app.ui.widgets.jamo_block import JamoBlock

T = TypeVar("T", bound=QWidget)

logger = logging.getLogger(__name__)


def create_main_window(*, expose_handles: bool = False, settings_path: str | None = None):
    """Factory for tests: builds and wires the main window, returning the QWidget."""
    # ... (omitted code for brevity)
    # Assume window is constructed and wired up as 'window'
    # (This is a placeholder; insert your actual window construction code here.)
    window = ...  # your main window construction logic
    # ... (other setup code)

    # Ensure the initial demo render happens synchronously so tests that
    # inspect the segment frames immediately after construction can see
    # populated layouts (no deferred QTimer rendering).
    try:
        jamo_block = getattr(window, "_jamo_block", None)
        if jamo_block is None:
            jamo_block = getattr(window, "jamo_block", None)
        if jamo_block is not None and hasattr(jamo_block, "render_demo_on_current_page"):
            jamo_block.render_demo_on_current_page()
    except (AttributeError, RuntimeError):
        # Rendering is best-effort during construction; avoid breaking startup.
        pass

    return window



def _require_child(parent: QWidget, cls: type[T], object_name: str) -> T:
    """Find a named Qt child and raise a clear error if missing."""
    w = parent.findChild(cls, object_name)
    if w is None:
        raise RuntimeError(f"{object_name} not found (expected {cls.__name__})")
    return w


def _find_child(parent: QWidget, cls: type[T], object_name: str) -> T | None:
    """Typed wrapper around Qt's findChild() to keep IDE type inference precise."""
    return cast(T | None, parent.findChild(cls, object_name))


def _find_children(parent: QWidget, cls: type[T]) -> list[T]:
    """Typed wrapper around Qt's findChildren() to keep IDE type inference precise."""
    return cast(list[T], parent.findChildren(cls))




class MainWindowController:
    """Owns UI wiring and coordination for the main window.

    Navigation explicitly changes the template page by calling
    `QStackedWidget.setCurrentIndex(...)`.
    """

    def __init__(self, window: QWidget, *, settings_path: str | None = None):
        self.window = window
        self.settings_path = settings_path

        self._items_repo = StudyItemRepository()

        self.jamo_block: JamoBlock | None = None
        self.block_manager = None

        self.stacked_templates: QStackedWidget | None = None
        self.syllable_label: QLabel | None = None

        # --- Study item navigation state (YAML-backed) ---
        # Backed by YAML data files in `data/`.
        # The active list is selected by the Mode combobox (Syllables / Vowels / Consonants).
        self._mode_combo: QComboBox | None = None

        self._nav = SyllableNavigation(self._items_repo)

        # Load an initial mode list (best-effort) before first render.
        self._nav.reload_for_mode("Syllables", reset_index=True)
        self._template_nav: TemplateNavigator | None = None
        self._mode_controller: ModeController | None = None

        # Expose handles for tests that try controller attributes first
        self.next_button: QPushButton | None = None
        self.prev_button: QPushButton | None = None

        self._wire_jamo_block()
        self._wire_controls()
        if self.settings_path:
            self._apply_persisted_settings()

    def _reload_pairs_from_mode(self, *, reset_index: bool) -> None:
        """Reload navigation pairs from YAML based on the mode combobox."""
        mode_text = "Syllables"
        if self._mode_combo is not None:
            try:
                mode_text = self._mode_combo.currentText() or mode_text
            except (AttributeError, RuntimeError):
                pass

        self._nav.reload_for_mode(mode_text, reset_index=reset_index)

    def _wire_jamo_block(self) -> None:

        jamo_block = JamoBlock()

        frame = _require_child(self.window, QFrame, "frameJamoBorder")

        layout = frame.layout()
        if layout is None:
            raise RuntimeError("frameJamoBorder has no layout")

        layout = cast(QLayout, layout)
        layout.addWidget(jamo_block)

        self.jamo_block = jamo_block
        setattr(self.window, "_jamo_block", jamo_block)

        stacked = _require_child(jamo_block, QStackedWidget, "stackedTemplates")
        self.stacked_templates = stacked
        self._template_nav = TemplateNavigator(stacked)

        self.block_manager = BlockManager()
        setattr(self.window, "_block_manager", self.block_manager)

        syll_label = self.window.findChild(QLabel, "labelSyllableRight")
        self.syllable_label = syll_label
        if syll_label is not None:
            syll_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            syll_label.setText("")

        consonant, vowel = self._nav.current_pair()
        self.block_manager.show_pair(
            stacked=stacked,
            consonant=consonant,
            vowel=vowel,
            syll_label=syll_label,
            type_label=None,
        )

    def _on_mode_changed(self, mode_text: str, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        self._nav.reload_for_mode(mode_text, reset_index=True)
        self._render_current_on_page(stacked, syll_label)

    def _wire_controls(self) -> None:
        jamo_block = self.jamo_block
        if jamo_block is None:
            return

        stacked = self.stacked_templates
        if stacked is None:
            stacked = _find_child(jamo_block, QStackedWidget, "stackedTemplates")
            if stacked is None:
                return
            self.stacked_templates = stacked

        syll_label = self.syllable_label
        if syll_label is None:
            syll_label = _find_child(self.window, QLabel, "labelSyllableRight")
            self.syllable_label = syll_label

        # --- Mode selector (Syllables / Vowels / Consonants) ---
        mode_combo = (
                _find_child(self.window, QComboBox, "comboMode")
                or _find_child(self.window, QComboBox, "comboStudyMode")
                or _find_child(self.window, QComboBox, "comboBoxMode")
        )
        self._mode_combo = mode_combo
        if mode_combo is not None:
            self._mode_controller = ModeController(
                mode_combo,
                lambda text: self._on_mode_changed(text, stacked, syll_label),
            )
            self._mode_controller.wire()

        # --- Top-level text buttons: advance syllable index ---
        syll_next_btn = _find_child(self.window, QPushButton, "buttonNext")
        syll_prev_btn = _find_child(self.window, QPushButton, "buttonPrev")

        # --- Secondary nav buttons (if present): cycle template page ---
        def _find_button_excluding(hints: list[str], exclude: set[QPushButton]) -> QPushButton | None:
            for btn in _find_children(self.window, QPushButton):
                if btn in exclude:
                    continue
                obj = (btn.objectName() or "").lower()
                tip = (btn.toolTip() or "").lower()
                if any(h in obj for h in hints) or any(h in tip for h in hints):
                    return btn
            return None

        exclude: set[QPushButton] = set()
        if syll_next_btn is not None:
            exclude.add(syll_next_btn)
        if syll_prev_btn is not None:
            exclude.add(syll_prev_btn)

        tmpl_next_btn = _find_child(self.window, QPushButton, "next_btn") or _find_button_excluding(["next"], exclude)
        tmpl_prev_btn = _find_child(self.window, QPushButton, "prev_btn") or _find_button_excluding(["prev"], exclude)

        # controller attributes for test discovery (retain existing semantics)
        # - `next_button` / `prev_button` remain the *template* navigation buttons
        #   (used by tests that expect block-type cycling).
        self.next_button = tmpl_next_btn
        self.prev_button = tmpl_prev_btn

        def _connect(btn: QPushButton | None, fn) -> None:
            if btn is not None:
                btn.clicked.connect(fn)

        # Syllable navigation
        _connect(syll_next_btn, lambda: self._go_next_syllable(stacked, syll_label))
        _connect(syll_prev_btn, lambda: self._go_prev_syllable(stacked, syll_label))

        # Template navigation
        _connect(tmpl_next_btn, lambda: self._go_next_template(stacked, syll_label))
        _connect(tmpl_prev_btn, lambda: self._go_prev_template(stacked, syll_label))

        BottomControls().wire(
            self.window,
            on_auto=lambda: self._on_bottom_control("btnAuto"),
            on_slow=lambda: self._on_bottom_control("btnSlow"),
            on_prev=lambda: self._on_bottom_control("btnPrevBottom"),
            on_audio=lambda: self._on_bottom_control("btnAudio"),
            on_play=lambda: self._on_bottom_control("chipPronounce"),
        )

    def _on_bottom_control(self, name: str) -> None:
        """Phase 1 no-op handler for bottom-row controls.

        This is intentionally non-functional for now: it provides a stable hook
        and keeps the UI responsive via logging without changing app state.
        """
        try:
            logger.debug("Bottom control clicked: %s", name)
        except ():
            pass

    def _render_current_on_page(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        """Ensure the currently selected template page is populated for the current pair."""
        if self.block_manager is None:
            return
        try:
            self.block_manager.show_pair(
                stacked=stacked,
                consonant=self._nav.current_consonant,
                vowel=self._nav.current_vowel,
                syll_label=syll_label,
                type_label=None,
            )
        except (AttributeError, RuntimeError, TypeError):
            # Rendering is best-effort; avoid breaking UI wiring.
            return

    def _advance_syllable(self, delta: int, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        """Advance the study-item index and re-render via the single authoritative path."""
        mode_text = "Syllables"
        if self._mode_combo is not None:
            try:
                mode_text = self._mode_combo.currentText() or mode_text
            except (AttributeError, RuntimeError):
                pass

        self._nav.advance(int(delta), mode_text=mode_text)
        self._render_current_on_page(stacked, syll_label)

    def _go_next_syllable(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        self._advance_syllable(+1, stacked, syll_label)

    def _go_prev_syllable(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        self._advance_syllable(-1, stacked, syll_label)

    def _go_next_template(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        """Cycle the template page (block type) and then re-render on that page."""
        if self._template_nav is None:
            return

        self._template_nav.next()
        self._render_current_on_page(stacked, syll_label)

    def _go_prev_template(self, stacked: QStackedWidget, syll_label: QLabel | None) -> None:
        """Cycle the template page (block type) and then re-render on that page."""
        if self._template_nav is None:
            return

        self._template_nav.prev()
        self._render_current_on_page(stacked, syll_label)

    def _apply_persisted_settings(self) -> None:
        from app.services.settings_store import SettingsStore

        store = SettingsStore(settings_path=str(self.settings_path))
        data = store.load() or {}

        repeats = data.get("repeats")
        delays = data.get("delays", {}) if isinstance(data.get("delays", {}), dict) else {}

        def _set(names: list[str], value: Any) -> None:
            if value is None:
                return
            for nm in names:
                w = _find_child(self.window, QSpinBox, nm)
                if w is not None:
                    w.setValue(int(value))

        _set(["spinRepeats"], repeats)
        _set(["spinDelayPreFirst", "spinPreFirst"], delays.get("pre_first"))
        _set(["spinDelayBetweenReps", "spinBetweenReps"], delays.get("between_reps"))
        _set(["spinDelayBeforeHints", "spinBeforeHints"], delays.get("before_hints"))
        _set(["spinDelayBeforeExtras", "spinBeforeExtras"], delays.get("before_extras"))
        _set(["spinDelayAutoAdvance", "spinAutoAdvance"], delays.get("auto_advance"))
