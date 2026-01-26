from __future__ import annotations

from typing import Optional, Callable
import re

from PyQt6.QtWidgets import QLabel, QPushButton, QRadioButton, QWidget

from app.domain.romanization_rr import romanize_cv, romanize_text
from app.domain.rr_hint_data import consonant_rr, vowel_rr


class RomanizationUiController:
    def __init__(
            self,
            *,
            window: QWidget,
            get_current_pair: Callable[[], tuple[str, str]],
            get_mode_text: Callable[[], str] | None = None,
            get_current_text: Callable[[], str] | None = None,
            on_hear: Callable[[], None],
    ) -> None:
        self._window = window
        self._get_current_pair = get_current_pair
        self._get_mode_text = get_mode_text
        self._get_current_text = get_current_text
        self._on_hear = on_hear
        self._show_cues = True

        self.label_value: Optional[QLabel] = None
        self.label_hint: Optional[QLabel] = None
        self.btn_hear: Optional[QPushButton] = None
        self.radio_cues: Optional[QRadioButton] = None

    def wire(self) -> None:
        self.label_value = self._window.findChild(QLabel, "labelRRValue")
        self.label_hint = self._window.findChild(QLabel, "labelRRHint")
        self.btn_hear = self._window.findChild(QPushButton, "btnRRHear")
        self.radio_cues = self._window.findChild(QRadioButton, "radioRRCues")
        if self.btn_hear is not None:
            self.btn_hear.clicked.connect(self._on_hear)
        if self.radio_cues is not None:
            try:
                self._show_cues = bool(self.radio_cues.isChecked())
            except Exception:
                self._show_cues = True
            self.radio_cues.toggled.connect(self._on_cues_toggled)
        self.update()

    def update(self) -> None:
        mode_text = ""
        if self._get_mode_text is not None:
            try:
                mode_text = (self._get_mode_text() or "").strip().lower()
            except Exception:
                mode_text = ""
        if mode_text == "vowels":
            consonant, vowel = self._get_current_pair()
            result = romanize_cv("", vowel)
        elif mode_text == "consonants":
            consonant, vowel = self._get_current_pair()
            result = romanize_cv(consonant, "")
        else:
            text = ""
            if self._get_current_text is not None:
                try:
                    text = (self._get_current_text() or "").strip()
                except Exception:
                    text = ""
            if len(text) > 1:
                result = romanize_text(text)
            else:
                consonant, vowel = self._get_current_pair()
                result = romanize_cv(consonant, vowel)
        if self.label_value is not None:
            self.label_value.setText(result.rr)
        if self.label_hint is not None:
            if self._show_cues:
                self.label_hint.setText(self._build_rr_cues(mode_text, result.hint))
                self.label_hint.setVisible(True)
            else:
                self.label_hint.setText(result.hint)
                self.label_hint.setVisible(True)

    def _on_cues_toggled(self, checked: bool) -> None:
        self._show_cues = bool(checked)
        self.update()

    def _build_rr_cues(self, mode_text: str, compact_hint: str) -> str:
        consonant, vowel = self._get_current_pair()
        blocks: list[str] = []
        if mode_text == "syllables":
            if consonant:
                cons_rr = consonant_rr(consonant)
                cons_hint = self._compact_with_best(romanize_cv(consonant, "").hint, cons_rr)
                cons_block = self._format_rr_block(cons_rr)
                blocks.append(self._format_section(cons_hint, cons_block))
            if vowel:
                vowel_rr_data = vowel_rr(vowel)
                vowel_hint = self._compact_with_best(romanize_cv("", vowel).hint, vowel_rr_data)
                vowel_block = self._format_rr_block(vowel_rr_data)
                blocks.append(self._format_section(vowel_hint, vowel_block))
            return "<br><br>".join([b for b in blocks if b])

        rr_data: dict[str, str] = {}
        if mode_text == "vowels":
            rr_data = vowel_rr(vowel)
        elif mode_text == "consonants":
            rr_data = consonant_rr(consonant)

        if mode_text != "vowels" and consonant:
            blocks.append(self._format_rr_block(consonant_rr(consonant)))
        if mode_text != "consonants" and vowel:
            blocks.append(self._format_rr_block(vowel_rr(vowel)))
        joined = "\n\n".join([b for b in blocks if b])
        if not joined:
            return compact_hint
        html_blocks = self._to_html(joined)
        compact_html = self._to_html(self._compact_with_best(compact_hint, rr_data))
        return f"<b>{compact_html}</b><br><br>{html_blocks}"

    @staticmethod
    def _format_rr_block(rr: dict[str, str]) -> str:
        if not rr:
            return ""
        lines: list[str] = []
        target = rr.get("target_sound", "").strip()
        alt = rr.get("alternative", "").strip()
        if target:
            lines.append(f"Target sound: {target}")
        if alt:
            lines.append(f"Alternative (less good, but common): {alt}")
        return "\n".join(lines)

    def _format_section(self, heading: str, block: str) -> str:
        heading_html = f"<b>{self._to_html(heading)}</b>" if heading else ""
        if not block:
            return heading_html
        block_html = self._to_html(block)
        if heading_html:
            return f"{heading_html}<br>{block_html}"
        return block_html

    @staticmethod
    def _compact_with_best(compact_hint: str, rr: dict[str, str]) -> str:
        if not compact_hint:
            return compact_hint
        best = rr.get("best_approx", "").strip()
        if not best or "as in" not in compact_hint:
            return compact_hint
        return re.sub(r"as in\\s+[^,.]+", best, compact_hint, count=1)

    @staticmethod
    def _to_html(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
