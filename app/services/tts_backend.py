from __future__ import annotations

import os
from typing import Optional

from app.services import tts_pronouncer
from tts.tts_service import TTSService


class HybridTTSBackend:
    """Prefer Google Cloud TTS, fall back to macOS/system voices."""

    def __init__(
        self,
        *,
        fallback: Optional[TTSService] = None,
        language_code: str = "ko-KR",
        voice_name: Optional[str] = None,
    ) -> None:
        self._fallback = fallback or TTSService()
        self._language_code = language_code
        self._voice_name = voice_name or os.environ.get("HANGUL_GCP_VOICE", "ko-KR-Standard-A")
        self._rate_wpm: int = 120

    def set_rate_wpm(self, wpm: int) -> None:
        try:
            self._rate_wpm = int(wpm)
        except Exception:
            self._rate_wpm = 120
        try:
            if hasattr(self._fallback, "set_rate_wpm"):
                self._fallback.set_rate_wpm(self._rate_wpm)
        except Exception:
            pass

    def _wpm_to_speaking_rate(self) -> float:
        # Map 40..160 WPM -> ~0.6..1.6 speaking_rate (matches ref behavior).
        wpm = max(40, min(160, int(self._rate_wpm)))
        return round(0.6 + (wpm - 40) * (1.0 / 120.0), 2)

    def pronounce_syllable(self, glyph: str, on_complete=None) -> None:
        if str(os.environ.get("HANGUL_TEST_MODE", "")).strip().lower() in ("1", "true", "yes", "on"):
            if callable(on_complete):
                try:
                    on_complete()
                except Exception:
                    pass
            return
        try:
            if not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
                hac = (os.environ.get("HANGUEL_APPLICATION_CREDENTIALS") or "").strip()
                if hac:
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = hac
            print("[TTS] Using Google Cloud voice: {}".format(self._voice_name))
            tts_pronouncer.pronounce(
                glyph,
                language_code=self._language_code,
                voice_name=self._voice_name,
                speaking_rate=self._wpm_to_speaking_rate(),
                play=True,
            )
        except Exception:
            try:
                print("[TTS] Falling back to system voice: {}".format(self._fallback.voice))
            except Exception:
                print("[TTS] Falling back to system voice")
            try:
                self._fallback.speak(glyph)
            except Exception:
                pass
        if callable(on_complete):
            try:
                on_complete()
            except Exception:
                pass
