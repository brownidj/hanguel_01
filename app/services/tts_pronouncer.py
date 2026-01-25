

"""Text-to-speech (TTS) pronunciation utilities.

This module is intentionally UI-agnostic: it does not depend on any QWidget
classes. Callers (e.g., main window / orchestrator) should invoke `pronounce()`
(or `ensure_cached_wav()`) and decide how/when to wire it to UI controls.

Primary responsibilities:
- Determine a stable cache filename for a requested utterance.
- Ensure a WAV exists on disk (cache hit/miss).
- Optionally synthesize missing audio (pluggable backend).
- Optionally play the WAV via QtMultimedia when available.

Design note:
Tests can inject a `synthesizer` callable into `ensure_cached_wav()` to avoid
network calls.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import hashlib
import os


# ----------------------------
# Public types
# ----------------------------


Synthesizer = Callable[[str], bytes]


@dataclass(frozen=True)
class TtsRequest:
    """A request to generate/locate audio for text."""

    text: str
    language_code: str = "ko-KR"
    voice_name: str = "ko-KR-Standard-A"
    speaking_rate: float | None = None


# ----------------------------
# Cache paths / filenames
# ----------------------------


def get_cache_dir() -> Path:
    """Return the directory used to store cached TTS WAV files.

    Priority:
    1) HANGUL_TTS_CACHE_DIR env var (absolute or relative)
    2) <project_root>/.cache/tts (if project root can be inferred)
    3) ~/.cache/hangul_01/tts

    The directory is created if it does not exist.
    """
    env = (os.environ.get("HANGUL_TTS_CACHE_DIR") or "").strip()
    if env:
        p = Path(env).expanduser()
        p.mkdir(parents=True, exist_ok=True)
        return p

    # Attempt a small, robust inference: if this file is inside the project, use
    # a sibling `.cache/tts` anchored at project root.
    here = Path(__file__).resolve()

    # Heuristic: walk upwards looking for a pyproject.toml or requirements.txt
    # (max 5 levels). If not found, fall back to user cache.
    project_root: Optional[Path] = None
    for i in range(1, 6):
        try:
            cand = here.parents[i]
        except IndexError:
            break
        if (cand / "pyproject.toml").exists() or (cand / "requirements.txt").exists():
            project_root = cand
            break

    if project_root is not None:
        p = project_root / ".cache" / "tts"
        p.mkdir(parents=True, exist_ok=True)
        return p

    p = Path.home() / ".cache" / "hangul_01" / "tts"
    p.mkdir(parents=True, exist_ok=True)
    return p


def cached_filename(
    text: str,
    language_code: str = "ko-KR",
    voice_name: str = "ko-KR-Standard-A",
    speaking_rate: float | None = None,
) -> str:
    """Return a stable cache filename for the given request.

    The exact string is designed to be deterministic and filesystem-safe.

    Format:
        tts_<sha1>_<lang>_<voice>.wav

    Where sha1 is computed over: "<lang>\n<voice>\n<text>" encoded as UTF-8.
    """
    # Avoid f-strings by user preference.
    material = "{}\n{}\n{}\n{}".format(language_code, voice_name, speaking_rate or "", text)
    digest = hashlib.sha1(material.encode("utf-8")).hexdigest()

    # Make voice safe for filenames.
    safe_voice = "".join([c if c.isalnum() or c in ("-", "_", ".") else "_" for c in voice_name])
    safe_lang = "".join([c if c.isalnum() or c in ("-", "_") else "_" for c in language_code])

    return "tts_{}_{}_{}.wav".format(digest, safe_lang, safe_voice)


def cached_path(req: TtsRequest) -> Path:
    """Return the full path to the cached WAV file for a request."""
    return get_cache_dir() / cached_filename(
        req.text,
        req.language_code,
        req.voice_name,
        req.speaking_rate,
    )


# ----------------------------
# Synthesis backends
# ----------------------------


def _google_cloud_synthesize_wav(req: TtsRequest) -> bytes:
    """Synthesize WAV bytes via Google Cloud Text-to-Speech.

    This is a best-effort backend.

    Requirements:
    - google-cloud-texttospeech installed
    - credentials provided via standard GOOGLE_APPLICATION_CREDENTIALS or env.

    Raises RuntimeError if the backend is unavailable.
    """
    try:
        from google.cloud import texttospeech  # type: ignore
    except Exception as e:
        raise RuntimeError("Google Cloud TTS backend unavailable: {}".format(e))

    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=req.text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=req.language_code,
        name=req.voice_name,
    )

    # LINEAR16 is standard WAV PCM.
    if req.speaking_rate is not None:
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=float(req.speaking_rate),
        )
    else:
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        )

    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config,
    )

    return bytes(response.audio_content)


def default_synthesizer(req: TtsRequest) -> bytes:
    """Default synthesis backend used when no synthesizer is injected.

    Currently attempts Google Cloud TTS. If unavailable, raises.
    """
    return _google_cloud_synthesize_wav(req)


# ----------------------------
# Cache ensure + playback
# ----------------------------


def ensure_cached_wav(
    text: str,
    *,
    language_code: str = "ko-KR",
    voice_name: str = "ko-KR-Standard-A",
    speaking_rate: float | None = None,
    synthesizer: Optional[Synthesizer] = None,
) -> Path:
    """Ensure a cached WAV exists for `text` and return its path.

    If the WAV already exists, returns immediately without calling the synthesizer.

    The `synthesizer` callable (if provided) must accept `text: str` and return
    WAV bytes.

    If `synthesizer` is None, `default_synthesizer()` will be used.
    """
    req = TtsRequest(
        text=text,
        language_code=language_code,
        voice_name=voice_name,
        speaking_rate=speaking_rate,
    )
    out_path = cached_path(req)

    if out_path.exists() and out_path.is_file() and out_path.stat().st_size > 0:
        return out_path

    # Synthesize and write atomically.
    if synthesizer is None:
        wav_bytes = default_synthesizer(req)
    else:
        wav_bytes = synthesizer(text)

    out_path.parent.mkdir(parents=True, exist_ok=True)

    tmp_path = out_path.with_suffix(out_path.suffix + ".tmp")
    with open(tmp_path, "wb") as f:
        f.write(wav_bytes)

    try:
        os.replace(str(tmp_path), str(out_path))
    except Exception:
        # Best-effort cleanup.
        try:
            if tmp_path.exists():
                tmp_path.unlink()
        except Exception:
            pass
        raise

    return out_path


def play_wav(path: Path) -> None:
    """Play a WAV file via QtMultimedia when available.

    This is intentionally best-effort. If QtMultimedia is unavailable (e.g., in
    headless tests), this function returns without raising.

    Note: the caller is responsible for keeping the Qt application alive.
    """
    try:
        from PyQt6.QtCore import QUrl  # type: ignore
        from PyQt6.QtMultimedia import QSoundEffect  # type: ignore
    except Exception:
        return

    try:
        eff = QSoundEffect()
        eff.setSource(QUrl.fromLocalFile(str(path)))
        eff.setLoopCount(1)
        eff.setVolume(1.0)
        eff.play()

        # IMPORTANT:
        # QSoundEffect must remain referenced; otherwise it may be GC'd.
        # We stash it on the module as a best-effort.
        globals()["_last_sound_effect"] = eff
    except Exception:
        return


def pronounce(
    text: str,
    *,
    language_code: str = "ko-KR",
    voice_name: str = "ko-KR-Standard-A",
    speaking_rate: float | None = None,
    synthesizer: Optional[Synthesizer] = None,
    play: bool = True,
) -> Path:
    """Ensure TTS audio exists for `text` and optionally play it.

    Returns the cached WAV path.

    In tests, pass `play=False` to avoid multimedia dependencies.
    """
    p = ensure_cached_wav(
        text,
        language_code=language_code,
        voice_name=voice_name,
        speaking_rate=speaking_rate,
        synthesizer=synthesizer,
    )
    if play:
        play_wav(p)
    return p


__all__ = [
    "TtsRequest",
    "Synthesizer",
    "get_cache_dir",
    "cached_filename",
    "cached_path",
    "ensure_cached_wav",
    "play_wav",
    "pronounce",
]
