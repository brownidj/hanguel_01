from __future__ import annotations

from typing import Callable, Optional

from PyQt6.QtWidgets import QLabel

from app.controllers.navigation_controller import NavigationController
from app.controllers.settings_controller import SettingsController
from app.controllers.syllable_navigation import SyllableNavigation
from app.domain.enums import DelaysConfig
from app.domain.hangul_compose import compose_cv


class PlaybackAdapter:
    """Small glue layer for playback callables."""

    def __init__(
        self,
        *,
        navigation: NavigationController | None,
        nav_fallback: SyllableNavigation,
        syllable_label: QLabel | None,
        settings: Optional[SettingsController],
    ) -> None:
        self._navigation = navigation
        self._nav_fallback = nav_fallback
        self._syllable_label = syllable_label
        self._settings = settings

    def set_navigation(self, navigation: NavigationController | None) -> None:
        self._navigation = navigation

    def set_syllable_label(self, label: QLabel | None) -> None:
        self._syllable_label = label

    def set_settings(self, settings: Optional[SettingsController]) -> None:
        self._settings = settings

    def current_glyph(self) -> str:
        if self._navigation is not None:
            return self._navigation.current_glyph()
        if self._syllable_label is not None:
            try:
                text = (self._syllable_label.text() or "").strip()
                if text:
                    return text
            except Exception:
                pass
        consonant, vowel = self._nav_fallback.current_pair()
        return compose_cv(consonant, vowel) or ""

    def current_repeats(self) -> int:
        if self._settings is not None:
            return self._settings.current_repeats()
        return 1

    def current_delays(self) -> DelaysConfig:
        if self._settings is not None:
            return self._settings.current_delays_ms()
        return DelaysConfig()
