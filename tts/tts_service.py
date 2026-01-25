# tts/tts_service.py
from __future__ import annotations
import os
import platform
import subprocess
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class _Voice:
    name: str
    lang: Optional[str]  # e.g., 'ko_KR', 'en_US'


def _list_macos_voices() -> List[_Voice]:
    """Return available macOS voices from `say -v '?'`."""
    try:
        out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, check=True)
        voices: List[_Voice] = []
        for raw in out.stdout.splitlines():
            line = raw.strip()
            if not line:
                continue
            no_sample = line.split('#', 1)[0].rstrip()
            parts = no_sample.split()
            if not parts:
                continue
            # Assume last token like ko_KR is a lang tag; name is the rest
            if len(parts) >= 2 and '_' in parts[-1]:
                lang = parts[-1]
                name = " ".join(parts[:-1]).strip()
            else:
                name = no_sample.strip()
                lang = None
            if name:
                voices.append(_Voice(name=name, lang=lang))
        return voices
    except Exception:
        return []


def _pick_best_korean(voices: List[_Voice], preferred_names: List[str]) -> Optional[str]:
    # 1) ENV override
    env_voice = os.environ.get("TTS_VOICE", "").strip()
    if env_voice:
        for v in voices:
            if v.name.lower() == env_voice.lower():
                return v.name
    # 2) Preferred names
    for pref in preferred_names:
        for v in voices:
            if v.name.lower() == pref.lower():
                return v.name
    # 3) Any ko_KR voice
    for v in voices:
        if (v.lang or "").lower() == "ko_kr":
            return v.name
    # 4) Fallback: system default (None)
    return None


class TTSService:
    """UI-agnostic TTS facade.

    macOS: uses `say`. Auto-selects a Korean voice (prefers 'Yuna') if present.
    Set TTS_VOICE=VoiceName to force a specific voice.
    """

    def __init__(self, preferred_lang: str = "ko_KR",
                 preferred_names: Optional[List[str]] = None,
                 rate: Optional[int] = None):
        self.rate = rate
        self.platform = platform.system().lower()
        if preferred_names is None:
            preferred_names = [
                "Yuna",
                "Flo (Korean (South Korea))",
                "Reed (Korean (South Korea))",
                "Sandy (Korean (South Korea))",
                "Grandma (Korean (South Korea))",
                "Eddy (Korean (South Korea))",
            ]
        self.voice: Optional[str] = None

        if self.platform == "darwin":
            voices = _list_macos_voices()
            picked = _pick_best_korean(voices, preferred_names)
            self.voice = picked
            if self.voice:
                print(f"[TTS] macOS voice selected: {self.voice}")
            else:
                print("[TTS] No Korean-specific voice found. Using system default.")
        else:
            print("[TTS] Non-macOS platform detected; using system default if available.")

    def speak(self, text: str) -> None:
        if not text:
            return
        if self.platform == "darwin":
            cmd = ["say"]
            if self.voice:
                cmd += ["-v", self.voice]
            if isinstance(self.rate, int) and self.rate > 0:
                cmd += ["-r", str(self.rate)]
            cmd += [text]
            try:
                subprocess.Popen(cmd)
            except Exception as e:
                print(f"[TTS] macOS say failed: {e}")
        else:
            # Minimal portable fallback
            try:
                import pyttsx3  # type: ignore
                engine = pyttsx3.init()
                if isinstance(self.rate, int) and self.rate > 0:
                    engine.setProperty("rate", self.rate)
                engine.say(text)
                engine.runAndWait()
            except Exception:
                print(f"[TTS] {self.platform}: unable to speak. Text was: {text}")

    def set_rate_wpm(self, wpm: int) -> None:
        try:
            self.rate = int(wpm)
        except Exception:
            pass

    def set_wpm(self, wpm: int) -> None:
        self.set_rate_wpm(wpm)
