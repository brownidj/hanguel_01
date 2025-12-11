import os
import sys

AUDIO_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "audio")

DEFAULT_VOICE = "ko-KR-Wavenet-A"
WPM_BUCKETS = [40, 80, 120, 160]

def _wpm_to_rate(wpm):
    # Map 40..160 WPM -> ~0.6..1.6 speaking_rate
    try:
        w = int(wpm)
    except Exception:
        w = 120
    return round(0.6 + (max(40, min(160, w)) - 40) * (1.0/120.0), 2)

from google.cloud import texttospeech
from google.oauth2 import service_account

def _client_from_env():
    # Prefer GOOGLE_APPLICATION_CREDENTIALS; fall back to HANGUEL_APPLICATION_CREDENTIALS
    gac = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    hac = os.environ.get("HANGUEL_APPLICATION_CREDENTIALS")
    try:
        if gac:
            return texttospeech.TextToSpeechClient()  # ADC will pick it up
        if hac and os.path.exists(hac):
            creds = service_account.Credentials.from_service_account_file(hac)
            return texttospeech.TextToSpeechClient(credentials=creds)
        # Last resort: default ADC (may work if you’ve authenticated via gcloud)
        return texttospeech.TextToSpeechClient()
    except Exception as e:
        print("Failed to create TTS client: {}".format(e), file=sys.stderr)
        sys.exit(1)

def synthesize_ko(text=u"가", outfile="sample_ko.wav",
                  voice_name=None, speaking_rate=1.0):
    client = _client_from_env()

    # Input text
    synthesis_input = texttospeech.SynthesisInput(text=text)

    # Voice: Korean
    # Pick a specific neural voice if you like, e.g., "ko-KR-Neural2-A" (varies by project/region)
    voice_params = {
        "language_code": "ko-KR",
    }
    if voice_name:
        voice_params["name"] = voice_name
    voice = texttospeech.VoiceSelectionParams(**voice_params)

    # Audio config: LINEAR16 → WAV
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.LINEAR16,
        speaking_rate=float(speaking_rate)
    )

    # Synthesize
    response = client.synthesize_speech(
        input=synthesis_input,
        voice=voice,
        audio_config=audio_config
    )

    # Write WAV bytes
    with open(outfile, "wb") as f:
        f.write(response.audio_content)

    print("Wrote WAV to: {}".format(outfile))

import yaml

def print_glyphs_from_yaml():
    yaml_files = [
        os.path.join("../data", "vowels.yaml"),
        os.path.join("../data", "consonants.yaml"),
        os.path.join("../data", "syllables.yaml"),
    ]

    for path in yaml_files:
        if not os.path.exists(path):
            print(f"Missing file: {path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

            def extract_glyphs(obj):
                if isinstance(obj, dict):
                    if "glyph" in obj and isinstance(obj["glyph"], str):
                        print(obj["glyph"].strip())
                    for v in obj.values():
                        extract_glyphs(v)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_glyphs(item)

            extract_glyphs(data)

def generate_all_assets(voice_name=None, wpm_list=None, force=False):
    """Generate .wav files for all glyphs in vowels, consonants, and syllables YAML files."""
    yaml_files = [
        os.path.join("../data", "vowels.yaml"),
        os.path.join("../data", "consonants.yaml"),
        os.path.join("../data", "syllables.yaml"),
    ]

    for path in yaml_files:
        if not os.path.exists(path):
            print(f"[WARN] Missing file: {path}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

            if voice_name is None:
                vname = DEFAULT_VOICE
            else:
                vname = voice_name
            wlist = WPM_BUCKETS if wpm_list is None else list(wpm_list)

            def extract_and_generate(obj):
                if isinstance(obj, dict):
                    if "glyph" in obj and isinstance(obj["glyph"], str):
                        g = obj["glyph"].strip()
                        if not g:
                            return
                        for wpm in wlist:
                            rate = _wpm_to_rate(wpm)
                            outfile = os.path.join(AUDIO_DIR, f"{g}__{vname}__{wpm}.wav")
                            synthesize_ko(g, outfile, vname, rate)
                    for v in obj.values():
                        extract_and_generate(v)
                elif isinstance(obj, list):
                    for item in obj:
                        extract_and_generate(item)

            extract_and_generate(data)

if __name__ == "__main__":
    # Usage:
    #   python3 utils/generate_wav.py                -> generate all assets into assets/audio
    #   python3 utils/generate_wav.py --force        -> regenerate all assets (ignore cache)
    #   python3 utils/generate_wav.py --sample 가 out.wav ko-KR-Wavenet-A 1.0
    args = sys.argv[1:]

    force = False
    if "--force" in args:
        force = True
        args.remove("--force")

    if len(args) > 0 and args[0] == "--sample":
        text = args[1] if len(args) > 1 else u"가"
        outfile = args[2] if len(args) > 2 else os.path.join(AUDIO_DIR, "sample_ko.wav")
        voice_name = args[3] if len(args) > 3 else None
        rate = float(args[4]) if len(args) > 4 else 1.0
        synthesize_ko(text, outfile, voice_name, rate, force=force)
    else:
        # bulk generation for vowels, consonants, syllables
        generate_all_assets(voice_name=None, wpm_list=WPM_BUCKETS)