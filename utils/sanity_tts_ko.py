import os
import sys

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

if __name__ == "__main__":
    # Usage: python3 sanity_tts_ko.py [text] [outfile] [voice_name] [rate]
    text = sys.argv[1] if len(sys.argv) > 1 else u"가"
    outfile = sys.argv[2] if len(sys.argv) > 2 else "sample_ko.wav"
    voice_name = sys.argv[3] if len(sys.argv) > 3 else None
    rate = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
    synthesize_ko(text, outfile, voice_name, rate)