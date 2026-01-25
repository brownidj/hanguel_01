from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Callable

from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QPushButton, QWidget, QToolTip

import logging

logger = logging.getLogger(__name__)

from app.controllers.examples_selector import ExamplesSelector
from app.controllers.examples_repository import ExampleItem
from app.services.tts_pronouncer import play_wav


class ExamplesUiController:
    """Owns Examples panel UI wiring and updates."""

    _HANGUL_PT = 36
    _META_PT = 14
    _HANGUL_WEIGHT = 900
    _META_WEIGHT = 500
    def __init__(
        self,
        *,
        window: QWidget,
        selector: ExamplesSelector,
        get_wpm: Optional[Callable[[], int]] = None,
    ) -> None:
        self._window = window
        self._selector = selector
        self._get_wpm = get_wpm
        self._offset = 0
        self._current_item: ExampleItem | None = None

        self.label_hangul: Optional[QLabel] = None
        self.label_hangul_plain: Optional[QLabel] = None
        self.label_rr: Optional[QLabel] = None
        self.label_gloss: Optional[QLabel] = None
        self.label_image: Optional[QLabel] = None
        self.btn_hear: Optional[QPushButton] = None

    def wire(self) -> None:
        self.label_hangul = self._window.findChild(QLabel, "labelExampleHangul")
        self.label_hangul_plain = self._window.findChild(QLabel, "labelExampleHangulPlain")
        self.label_rr = self._window.findChild(QLabel, "labelExampleRR")
        self.label_gloss = self._window.findChild(QLabel, "labelExampleGloss")
        self.label_image = self._window.findChild(QLabel, "labelExampleImage")
        self.btn_hear = self._window.findChild(QPushButton, "btnExampleHear")
        if self.btn_hear is not None:
            self.btn_hear.clicked.connect(self._on_hear_clicked)
        try:
            setter = getattr(QToolTip, "setShowDelay", None)
            if callable(setter):
                setter(300)
        except (AttributeError, TypeError, RuntimeError) as e:
            logger.debug("Failed to configure tooltip delay: %s", e)

        self.update()

    def update(self) -> None:
        self._offset = 0
        self._apply_selected(self._selector.pick_example())

    def _apply_selected(self, item: ExampleItem | None) -> None:
        self._current_item = item
        if str(os.environ.get("HANGUL_DEBUG_EXAMPLES", "")).strip().lower() in ("1", "true", "yes", "on"):
            try:
                glyph = item.hangul if item is not None else ""
                print("[DEBUG] Example render: {}".format(glyph))
            except (AttributeError, TypeError):
                logger.debug("Failed to read example glyph for debug logging")
        if self.label_hangul is not None:
            if item:
                # Use rich text so only the Hangul line is bold.
                hangul = self._highlight_syllable(item.hangul, item.starts_with_syllable)
                text = (
                    "<span style=\"font-size:{}pt; font-weight:{};\">{}</span>"
                    "<br><span style=\"font-size:{}pt; font-weight:{};\">Pronunciation: {}</span>"
                    "<br><span style=\"font-size:{}pt; font-weight:{};\">Meaning: {}</span>"
                ).format(
                    self._HANGUL_PT,
                    self._HANGUL_WEIGHT,
                    hangul,
                    self._META_PT,
                    self._META_WEIGHT,
                    self._escape_html(item.rr),
                    self._META_PT,
                    self._META_WEIGHT,
                    self._escape_html(item.gloss_en),
                )
            else:
                text = ""
            self.label_hangul.setText(text)
        # Keep a plain-text mirror for tests/tooling that read QLabel.text().
        if self.label_hangul_plain is not None:
            self.label_hangul_plain.setText(item.hangul if item else "")
        if self.label_image is not None:
            self._set_image(item)

    def _on_hear_clicked(self) -> None:
        item = self._current_item
        if item is None:
            return
        glyph = (item.hangul or "").strip()
        if not glyph:
            return
        wpm = 120
        if self._get_wpm is not None:
            try:
                wpm = int(self._get_wpm())
            except (TypeError, ValueError):
                logger.debug("Invalid WPM from settings; using default")
                wpm = 120
        bucket = self._nearest_wpm_bucket(wpm)
        filename = f"{glyph}__ko-KR-Wavenet-A__{bucket}.wav"
        path = Path(__file__).resolve().parents[2] / "assets" / "audio" / filename
        if not path.exists():
            logger.debug("Example audio missing: %s", path)
            return
        try:
            play_wav(path)
        except (RuntimeError, OSError) as e:
            logger.warning("Failed to play example audio %s: %s", path, e)

    @staticmethod
    def _nearest_wpm_bucket(wpm: int) -> int:
        buckets = (40, 80, 120, 160)
        return min(buckets, key=lambda b: abs(b - int(wpm)))

    @staticmethod
    def _escape_html(text: str) -> str:
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )

    def _highlight_syllable(self, hangul: str, syllable: str) -> str:
        escaped = self._escape_html(hangul)
        target = (syllable or "").strip()
        if not target:
            return escaped
        target_escaped = self._escape_html(target)
        marker = f"<span style=\"color:#d32f2f;\">{target_escaped}</span>"
        return escaped.replace(target_escaped, marker, 1)

    def _set_image(self, item: ExampleItem | None) -> None:
        if self.label_image is None:
            return
        if item is None:
            self.label_image.setText("No image yet")
            self.label_image.setPixmap(QPixmap())
            self.label_image.setToolTip("")
            return
        filename = item.image_filename
        if not filename:
            filename = self._guess_filename(item)
        if not filename:
            self.label_image.setText("No image yet")
            self.label_image.setPixmap(QPixmap())
            self.label_image.setToolTip(item.image_prompt or "")
            return
        path = Path(__file__).resolve().parents[2] / "assets" / "images" / "examples" / filename
        if not path.exists():
            self.label_image.setText("No image yet")
            self.label_image.setPixmap(QPixmap())
            self.label_image.setToolTip(item.image_prompt or "")
            logger.debug("Example image missing: %s", path)
            return
        pixmap = QPixmap(str(path))
        if pixmap.isNull():
            self.label_image.setText("No image yet")
            self.label_image.setPixmap(QPixmap())
            self.label_image.setToolTip(item.image_prompt or "")
            logger.warning("Failed to load example image: %s", path)
            return
        target = self.label_image.size()
        if not target.isValid():
            target = QSize(160, 160)
        pixmap = pixmap.scaled(target, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.label_image.setPixmap(pixmap)
        self.label_image.setText("")
        self.label_image.setToolTip(item.image_prompt or "")

    @staticmethod
    def _guess_filename(item: ExampleItem) -> str | None:
        gloss = item.gloss_en.strip().lower()
        if not gloss:
            return None
        chars = []
        for ch in gloss:
            if ch.isalnum():
                chars.append(ch)
            else:
                if not chars or chars[-1] != "_":
                    chars.append("_")
        slug = "".join(chars).strip("_")
        if not slug:
            return None
        return "{}.png".format(slug)
