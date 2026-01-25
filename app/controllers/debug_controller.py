from __future__ import annotations

import os
from typing import Optional

from app.ui.widgets.jamo_block import JamoBlock


class DebugController:
    """Owns optional debug hooks toggled by environment flags."""

    def __init__(self, *, jamo_block: Optional[JamoBlock]) -> None:
        self._jamo_block = jamo_block

    def dump_jamo_if_enabled(self) -> None:
        if self._jamo_block is None:
            return
        if str(os.getenv("HANGUL_DEBUG_JAMO", "")).strip().lower() not in ("1", "true", "yes", "on"):
            return
        try:
            self._jamo_block.debug_dump_current_template(prefix="[DEBUG]")
        except Exception:
            pass
