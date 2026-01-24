from __future__ import annotations

import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QFrame, QStackedWidget

from app.domain.hangul_compose import compose_cv

logger = logging.getLogger(__name__)


class BlockManager:
    """Places consonant/vowel labels onto the current template page.

    The test suite expects this name to exist and `show_pair(...)` to populate
    the current page segment frames.
    """

    def show_pair(
            self,
            *,
            stacked: QStackedWidget,
            consonant: str,
            vowel: str,
            syll_label: QLabel | None = None,
            type_label: QLabel | None = None,
    ) -> None:
        # --- Set syllable label if possible ---
        if syll_label is not None:
            c = (consonant or "").strip()
            v = (vowel or "").strip()

            if c and v and c != "∅" and v != "∅":
                syll_label.setText(compose_cv(c, v))
            elif c and c != "∅":
                syll_label.setText(c)
            elif v and v != "∅":
                syll_label.setText(v)
            else:
                syll_label.setText("")

        page = stacked.currentWidget()
        if page is None:
            return

        def _set_frame_text(frame_suffix: str, text: str) -> None:
            for fr in page.findChildren(QFrame):
                obj = (fr.objectName() or "")
                if not obj.endswith(frame_suffix):
                    continue

                labels = fr.findChildren(QLabel)
                if labels:
                    lbl = labels[0]
                else:
                    lbl = QLabel(fr)
                    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    lay = fr.layout()
                    if lay is not None:
                        lay.addWidget(lbl)

                lbl.setText(text)
                lbl.setVisible(True)

        _set_frame_text("segmentTop", consonant)
        _set_frame_text("segmentMiddle", vowel)
        _set_frame_text("segmentBottom", "∅")

        if type_label is not None:
            try:
                type_label.setText(str(stacked.currentIndex()))
            except (AttributeError, RuntimeError, TypeError):
                pass