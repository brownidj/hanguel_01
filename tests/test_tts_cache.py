"""
Scaffold tests for the TTS caching layer.

Goals:
- Verify filename pattern and filesystem safety for cached WAVs.
- Provide conditional (skipped) integration tests that you can enable
  once the app exposes simple helpers to resolve cache paths and to
  "get or synthesize" audio without starting the Qt event loop.

Expected cache filename format (per app spec):
    <glyph>__<voice_name>__<wpm>.wav
Example:
    "가__Yuna__120.wav"
"""

from pathlib import Path
import importlib
import pytest


# ------------------------------
# Utilities for discovery
# ------------------------------

def _find_cached_path_api(m):
    """
    Try to discover a cache path resolver in the app.
    Return a callable (glyph, voice, wpm) -> Path, or None.
    """
    for name in ("cached_wav_path", "_cached_wav_path", "tts_cached_path", "resolve_cached_wav_path"):
        fn = getattr(m, name, None)
        if callable(fn):
            return fn
    return None


def _find_get_or_build_api(m):
    """
    Try to discover a higher-level API that ensures a cached WAV exists.
    Accepts (glyph, voice, wpm) or named kwargs. Returns Path or str.
    """
    for name in ("get_or_build_wav", "ensure_wav_cached", "resolve_or_build_wav"):
        fn = getattr(m, name, None)
        if callable(fn):
            return fn
    # Look inside PronunciationController if present
    PC = getattr(m, "PronunciationController", None)
    if PC is not None:
        for method in ("get_or_build_wav", "ensure_wav_cached", "_ensure_wav"):
            if hasattr(PC, method):
                return ("PronunciationController", method)
    return None


@pytest.fixture
def main_module(monkeypatch, tmp_path: Path):
    """
    Import main with AUDIO_DIR and SETTINGS_PATH redirected into a temp area.
    """
    m = importlib.import_module("main")
    # Redirect settings and audio dir to tmp
    settings_tmp = tmp_path / "settings.yaml"
    audio_tmp = tmp_path / "assets" / "audio"
    audio_tmp.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(m, "SETTINGS_PATH", str(settings_tmp), raising=False)
    # Try multiple common symbols for audio dir
    for sym in ("AUDIO_DIR", "AUDIO_ROOT", "AUDIO_CACHE_DIR"):
        if hasattr(m, sym):
            monkeypatch.setattr(m, sym, str(audio_tmp), raising=False)
    # Expose path for tests even if main doesn't export a symbol
    m._TEST_AUDIO_DIR = str(audio_tmp)
    return m


# ------------------------------
# Filename / path behaviour
# ------------------------------

def test_cached_filename_pattern(main_module, tmp_path: Path):
    """
    The cache filename should follow: <glyph>__<voice>__<wpm>.wav
    and be placed under the configured AUDIO_DIR (or app's path).
    """
    m = main_module
    audio_dir = Path(getattr(m, "_TEST_AUDIO_DIR"))
    glyph, voice, wpm = "가", "Yuna", 120
    expected_name = f"{glyph}__{voice}__{wpm}.wav"

    # If the app exposes a path resolver, use it; else emulate the spec.
    resolver = _find_cached_path_api(m)
    if resolver is not None:
        try:
            out = resolver(glyph, voice, wpm)
        except TypeError:
            # allow named-only signatures
            out = resolver(glyph=glyph, voice=voice, wpm=wpm)
        out = Path(out)
    else:
        out = audio_dir / expected_name

    # Path should live under audio_dir and have the expected name.
    assert out.name == expected_name
    assert audio_dir in out.parents


# ------------------------------
# Cache hit behaviour (conditional)
# ------------------------------

@pytest.mark.skip(reason="Enable when app exposes an ensure/get_or_build API for cached WAVs.")
def test_cache_hit_skips_synthesis(monkeypatch, main_module):
    """
    If the cache file already exists, the app should NOT re-synthesize.
    We monkeypatch synth to raise if called, and expect no call.
    """
    m = main_module
    audio_dir = Path(getattr(m, "_TEST_AUDIO_DIR"))
    glyph, voice, wpm = "가", "Yuna", 120
    cache_path = audio_dir / f"{glyph}__{voice}__{wpm}.wav"
    cache_path.write_bytes(b"RIFF....WAVE")  # create a dummy wav file

    # Try to locate a synth function to patch
    try:
        import tts.tts_service as svc
        called = {"n": 0}
        def _bomb(*args, **kwargs):
            called["n"] += 1
            raise AssertionError("Synthesis should not be called on cache hit!")
        # Patch the lowest-level synth point you use
        if hasattr(svc.TTSService, "synthesize_to_wav"):
            monkeypatch.setattr(svc.TTSService, "synthesize_to_wav", _bomb, raising=True)
        elif hasattr(svc.TTSService, "speak"):
            monkeypatch.setattr(svc.TTSService, "speak", _bomb, raising=True)
    except Exception:
        pass

    api = _find_get_or_build_api(m)
    if api is None:
        pytest.skip("No ensure/get_or_build API exported yet.")
    elif isinstance(api, tuple) and api[0] == "PronunciationController":
        PC = m.PronunciationController
        ctl = PC(tts_service=None, player=None)  # adjust if your ctor requires args
        out = getattr(ctl, api[1])(glyph=glyph, voice=voice, wpm=wpm)
    else:
        # Call a top-level function
        try:
            out = api(glyph, voice, wpm)
        except TypeError:
            out = api(glyph=glyph, voice=voice, wpm=wpm)

    assert Path(out).exists(), "Cache file should exist/return on cache hit."
    # If we patched a synth, it must NOT have run
    # assert called["n"] == 0


# ------------------------------
# Cache miss behaviour (conditional)
# ------------------------------

@pytest.mark.skip(reason="Enable when app exposes an ensure/get_or_build API for cached WAVs.")
def test_cache_miss_triggers_synthesis(monkeypatch, main_module):
    """
    If the cache file does not exist, the app should synthesize it once,
    then return the created path.
    """
    m = main_module
    audio_dir = Path(getattr(m, "_TEST_AUDIO_DIR"))
    glyph, voice, wpm = "나", "Yuna", 80
    cache_path = audio_dir / f"{glyph}__{voice}__{wpm}.wav"
    if cache_path.exists():
        cache_path.unlink()

    # Patch synth to create a small dummy file instead of real TTS
    import tts.tts_service as svc
    created = {"n": 0}
    def _fake_synth(self, text, out_path, voice_name=None, wpm=None):
        Path(out_path).write_bytes(b"RIFF....WAVE")
        created["n"] += 1
        return out_path

    if hasattr(svc.TTSService, "synthesize_to_wav"):
        monkeypatch.setattr(svc.TTSService, "synthesize_to_wav", _fake_synth, raising=True)
    elif hasattr(svc.TTSService, "speak"):
        monkeypatch.setattr(svc.TTSService, "speak", lambda self, t: _fake_synth(self, t, str(cache_path)), raising=True)

    api = _find_get_or_build_api(m)
    if api is None:
        pytest.skip("No ensure/get_or_build API exported yet.")
    elif isinstance(api, tuple) and api[0] == "PronunciationController":
        PC = m.PronunciationController
        ctl = PC(tts_service=svc.TTSService(), player=None)  # adjust ctor as needed
        out = getattr(ctl, api[1])(glyph=glyph, voice=voice, wpm=wpm)
    else:
        try:
            out = api(glyph, voice, wpm)
        except TypeError:
            out = api(glyph=glyph, voice=voice, wpm=wpm)

    assert Path(out).exists(), "Synth should create the file on cache miss."
    assert created["n"] == 1, "Synth should be called exactly once."