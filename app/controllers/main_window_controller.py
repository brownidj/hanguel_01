from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QPushButton, QStackedWidget, QWidget

# from app.domain.hangul_compose import compose_cv
from app.controllers.bottom_controls import BottomControls
from app.controllers.debug_controller import DebugController
from app.controllers.drawer_ui_controller import DrawerUiController
from app.controllers.examples_repository import ExamplesRepository
from app.controllers.examples_selector import ExamplesSelector
from app.controllers.examples_ui_controller import ExamplesUiController
from app.controllers.jamo_block_controller import JamoBlockController
from app.controllers.consonant_sidebar_controller import ConsonantSidebarController
from app.controllers.mode_persistence_controller import ModePersistenceController
from app.controllers.mode_ui_controller import ModeUiController
from app.controllers.navigation_controller import NavigationController
from app.controllers.notes_ui_controller import NotesUiController
from app.controllers.playback_adapter import PlaybackAdapter
from app.controllers.playback_ui_controller import PlaybackUiController
from app.controllers.pronunciation_controller import PronunciationController
from app.controllers.romanization_ui_controller import RomanizationUiController
from app.controllers.rr_cues_persistence_controller import RrCuesPersistenceController
from app.controllers.settings_ui_controller import SettingsUiController
from app.controllers.study_item_repository import StudyItemRepository
from app.controllers.playback_controls_controller import set_controls_for_repeats_locked
from app.controllers.syllable_navigation import SyllableNavigation
from app.controllers.syllable_index_ui_controller import SyllableIndexUiController
from app.controllers.layout_stretch_controller import LayoutStretchController
from app.domain.hangul_compose import compose_cv
from app.services.tts_backend import HybridTTSBackend
from app.ui.utils.qt_find import find_child

_find_child = find_child




class MainWindowController:
    """Owns UI wiring and coordination for the main window.

    Navigation explicitly changes the template page by calling
    `QStackedWidget.setCurrentIndex(...)`.
    """

    def __init__(self, window: QWidget, *, settings_path: str | None = None):
        self.window = window
        self.settings_path = settings_path

        self._items_repo = StudyItemRepository()

        self._jamo_block_controller: JamoBlockController | None = None
        self.jamo_block = None
        self.block_manager = None

        self.stacked_templates: QStackedWidget | None = None
        self.syllable_label: QLabel | None = None

        # --- Study item navigation state (YAML-backed) ---
        # Backed by YAML data files in `data/`.
        # The active list is selected by the Mode combobox (Syllables / Vowels / Consonants).
        self._nav = SyllableNavigation(self._items_repo)

        # Load an initial mode list (best-effort) before first render.
        self._nav.reload_for_mode("Vowels", reset_index=True)
        self._navigation: NavigationController | None = None
        self._mode_ui: ModeUiController | None = None
        self._pronouncer: PronunciationController | None = None
        self._drawer_ui: DrawerUiController | None = None
        self._settings_controller = None
        self._settings_store = None
        self._playback_ui: PlaybackUiController | None = None
        self._playback_adapter: PlaybackAdapter | None = None
        self._settings_ui: SettingsUiController | None = None
        self._wpm_controller = None
        self._debug_controller: DebugController | None = None
        self._rr_ui: RomanizationUiController | None = None
        self._mode_persistence: ModePersistenceController | None = None
        self._rr_cues_persistence: RrCuesPersistenceController | None = None
        self._notes_ui: NotesUiController | None = None
        self._syllable_index_ui: SyllableIndexUiController | None = None
        self._consonant_sidebar: ConsonantSidebarController | None = None
        self._examples_repo: ExamplesRepository | None = None
        self._examples_selector: ExamplesSelector | None = None
        self._examples_ui: ExamplesUiController | None = None

        # Expose handles for tests that try controller attributes first
        self.next_button: QPushButton | None = None
        self.prev_button: QPushButton | None = None

        self._init_pronouncer()
        self._wire_jamo_block()
        self._debug_controller = DebugController(jamo_block=self.jamo_block)
        self._debug_controller.dump_jamo_if_enabled()
        self._wire_controls()
        self._wire_drawer()

    def _init_pronouncer(self) -> None:
        try:
            self._pronouncer = PronunciationController(HybridTTSBackend())
        except Exception:
            self._pronouncer = None

        try:
            if self._pronouncer is None:
                self._playback_ui = None
                return

            def _tts_play(glyph: str, on_done) -> None:
                self._pronouncer.pronounce_syllable(glyph, on_complete=on_done)

            def _next_item() -> None:
                self._go_next_syllable()

            def _prev_item() -> None:
                self._go_prev_syllable()

            self._playback_adapter = PlaybackAdapter(
                navigation=self._navigation,
                nav_fallback=self._nav,
                syllable_label=self.syllable_label,
                settings=self._settings_controller,
            )
            self._playback_ui = PlaybackUiController(
                window=self.window,
                tts_play=_tts_play,
                get_glyph=self._playback_adapter.current_glyph,
                get_repeats=self._playback_adapter.current_repeats,
                get_delays=self._playback_adapter.current_delays,
                on_next=_next_item,
                on_prev=_prev_item,
            )
        except Exception:
            self._playback_ui = None

    def _current_mode_text(self) -> str:
        if self._mode_ui is None:
            return "Syllables"
        return self._mode_ui.current_text()

    def _wire_jamo_block(self) -> None:
        self._jamo_block_controller = JamoBlockController(
            window=self.window,
            get_current_pair=self._nav.current_pair,
        )
        consonant, vowel = self._nav.current_pair()
        self._jamo_block_controller.wire(
            initial_consonant=consonant,
            initial_vowel=vowel,
        )

        self.jamo_block = self._jamo_block_controller.jamo_block
        self.stacked_templates = self._jamo_block_controller.stacked
        self.block_manager = self._jamo_block_controller.block_manager
        self.syllable_label = self._jamo_block_controller.syllable_label

        if self.block_manager is None or self.stacked_templates is None:
            return
        self._navigation = NavigationController(
            nav=self._nav,
            block_manager=self.block_manager,
            stacked=self.stacked_templates,
            syllable_label=self.syllable_label,
            get_mode_text=self._current_mode_text,
            compose_cv=compose_cv,
        )
        self._navigation.render_current()
        if self._playback_adapter is not None:
            self._playback_adapter.set_navigation(self._navigation)
            self._playback_adapter.set_syllable_label(self.syllable_label)

    def _wire_controls(self) -> None:
        jamo_block = self.jamo_block
        if jamo_block is None:
            return

        # --- Mode selector (Syllables / Vowels / Consonants) ---
        self._mode_ui = ModeUiController(window=self.window, navigation=self._navigation)
        self._mode_ui.wire()
        store = self._ensure_settings_store()
        if self._mode_ui.combo is not None:
            self._mode_persistence = ModePersistenceController(
                combo=self._mode_ui.combo,
                settings_store=store,
            )
            self._mode_persistence.wire()
        if self._navigation is not None:
            self._navigation.on_mode_changed(self._mode_ui.current_text())

        self._rr_ui = RomanizationUiController(
            window=self.window,
            get_current_pair=self._nav.current_pair,
            get_mode_text=self._current_mode_text,
            get_current_text=self._navigation.current_glyph if self._navigation is not None else (lambda: ""),
            on_hear=self._on_listen_clicked,
        )
        self._rr_ui.wire()
        if self._navigation is not None:
            self._navigation.set_on_item_changed(self._rr_ui.update)
        if self._rr_ui.radio_cues is not None:
            self._rr_cues_persistence = RrCuesPersistenceController(
                radio=self._rr_ui.radio_cues,
                settings_store=store,
            )
            self._rr_cues_persistence.wire()

        self._notes_ui = NotesUiController(
            window=self.window,
            get_mode_text=self._current_mode_text,
            get_current_pair=self._nav.current_pair,
        )
        self._notes_ui.wire()
        if self._navigation is not None:
            self._navigation.add_on_item_changed(self._notes_ui.update)

        self._consonant_sidebar = ConsonantSidebarController(
            window=self.window,
            get_mode_text=self._current_mode_text,
            get_current_pair=self._nav.current_pair,
            repo=self._items_repo,
        )
        self._consonant_sidebar.wire()
        if self._navigation is not None:
            self._navigation.add_on_item_changed(self._consonant_sidebar.update)

        self._syllable_index_ui = SyllableIndexUiController(
            window=self.window,
            navigation=self._nav,
            get_mode_text=self._current_mode_text,
        )
        self._syllable_index_ui.wire()
        if self._navigation is not None:
            self._navigation.add_on_item_changed(self._syllable_index_ui.update)

        self._examples_repo = ExamplesRepository()
        self._examples_selector = ExamplesSelector(
            get_mode_text=self._current_mode_text,
            get_current_pair=self._nav.current_pair,
            get_current_index=self._nav.current_index,
            repository=self._examples_repo,
        )
        self._examples_ui = ExamplesUiController(
            window=self.window,
            selector=self._examples_selector,
            get_wpm=self._ensure_settings_store().get_wpm,
        )
        self._examples_ui.wire()
        if self._navigation is not None:
            self._navigation.add_on_item_changed(self._examples_ui.update)

        LayoutStretchController(
            window=self.window,
            layout_name="layoutHintsExamplesRow",
            stretches=(13, 7),
        ).wire()

        # --- Top-level text buttons: advance syllable index ---
        syll_next_btn = _find_child(self.window, QPushButton, "buttonNext")
        syll_prev_btn = _find_child(self.window, QPushButton, "buttonPrev")

        # controller attributes for test discovery
        self.next_button = syll_next_btn
        self.prev_button = syll_prev_btn

        def _connect(btn: QPushButton | None, fn) -> None:
            if btn is not None:
                btn.clicked.connect(fn)

        # Syllable navigation
        _connect(syll_next_btn, self._go_next_syllable)
        _connect(syll_prev_btn, self._go_prev_syllable)

        BottomControls().wire(
            self.window,
            on_auto=self._on_auto_clicked,
            on_slow=self._on_slow_clicked,
            on_prev=self._on_chip_prev,
            on_play=self._on_listen_clicked,
            on_next=self._on_chip_next,
        )
        if self._playback_ui is not None:
            self._playback_ui.init_chips()
        # Ensure controls start enabled (some Qt stylesheets may retain disabled state).
        set_controls_for_repeats_locked(self.window, False)

        self._wire_settings_controls()

    def _on_listen_clicked(self) -> None:
        if self._playback_ui is None:
            return
        self._playback_ui.on_listen_clicked()

    def _on_chip_next(self) -> None:
        if self._playback_ui is None:
            return
        self._playback_ui.on_chip_next()

    def _on_chip_prev(self) -> None:
        if self._playback_ui is None:
            return
        self._playback_ui.on_chip_prev()

    def _on_auto_clicked(self) -> None:
        if self._playback_ui is None:
            return
        self._playback_ui.on_auto_clicked()

    def _on_slow_clicked(self) -> None:
        if self._wpm_controller is None:
            return
        self._wpm_controller.on_slow_clicked()

    def _wire_drawer(self) -> None:
        try:
            self._drawer_ui = DrawerUiController(window=self.window)
            self._drawer_ui.wire()
        except Exception:
            pass

    def _wire_settings_controls(self) -> None:
        try:
            store = self._ensure_settings_store()
            self._settings_ui = SettingsUiController(window=self.window, settings_store=store)
            self._settings_ui.set_pronouncer(self._pronouncer)
            self._settings_ui.wire()
            if self.settings_path:
                self._settings_ui.apply_persisted_settings()
            self._settings_controller = self._settings_ui.settings_controller
            self._wpm_controller = self._settings_ui.wpm_controller
            if self._playback_adapter is not None:
                self._playback_adapter.set_settings(self._settings_controller)
        except Exception:
            self._settings_controller = None
            self._wpm_controller = None
            self._settings_ui = None

    def _ensure_settings_store(self):
        if self._settings_store is None:
            from app.services.settings_store import SettingsStore
            self._settings_store = (
                SettingsStore(settings_path=str(self.settings_path))
                if self.settings_path
                else SettingsStore()
            )
        return self._settings_store

    def _go_next_syllable(self) -> None:
        if self._navigation is None:
            return
        self._navigation.go_next()

    def _go_prev_syllable(self) -> None:
        if self._navigation is None:
            return
        self._navigation.go_prev()

    def _go_next_template(self) -> None:
        if self._jamo_block_controller is None:
            return
        self._jamo_block_controller.go_next_template()

    def _go_prev_template(self) -> None:
        if self._jamo_block_controller is None:
            return
        self._jamo_block_controller.go_prev_template()
