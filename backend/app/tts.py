import os
from typing import Literal
import azure.cognitiveservices.speech as speechsdk

AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY", "")
AZURE_TTS_ENDPOINT = os.getenv("AZURE_TTS_ENDPOINT", "")

def synthesize_podcast(script: str, out_path: str, provider: Literal["azure"]="azure"):
    if provider != "azure":
        # Extend here for "local" if desired
        raise RuntimeError("Only Azure TTS is configured in this build.")

    if not AZURE_TTS_KEY or not AZURE_TTS_ENDPOINT:
        raise RuntimeError("Azure TTS ENV not set (AZURE_TTS_KEY, AZURE_TTS_ENDPOINT).")

    # Choose two voices for duo; otherwise single voice
    # You can tune these for gender/accent variety
    voice_1 = "en-US-JennyNeural"
    voice_2 = "en-US-GuyNeural"

    # Split the script into turns if we find "Host:" or "Speaker"
    lines = [l.strip() for l in script.splitlines() if l.strip()]
    chunks = []
    cur_voice = voice_1
    for ln in lines:
        if ln.lower().startswith(("host:", "speaker a:", "speaker 1:", "narrator:")):
            cur_voice = voice_1
            text = ln.split(":", 1)[1].strip() if ":" in ln else ln
        elif ln.lower().startswith(("guest:", "speaker b:", "speaker 2:")):
            cur_voice = voice_2
            text = ln.split(":", 1)[1].strip() if ":" in ln else ln
        else:
            text = ln
        chunks.append((cur_voice, text))

    # SSML per chunk → stitch by appending to single file (SDK handles stream)
    speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, endpoint=AZURE_TTS_ENDPOINT)
    audio_config = speechsdk.audio.AudioOutputConfig(filename=out_path)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # Concatenate into a single SSML to ensure one output file write
    ssml_body = ""
    for voice, text in chunks:
        ssml_body += f"""
            <voice name="{voice}">
              <prosody rate="0%" pitch="0%">{_escape_xml(text)}</prosody>
            </voice>
        """

    ssml = f"""<speak version="1.0" xml:lang="en-US">
        {ssml_body}
    </speak>"""

    result = synthesizer.speak_ssml_async(ssml).get()
    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        raise RuntimeError(f"Azure TTS failed: {result.reason}")

def _escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
         .replace('"', "&quot;")
         .replace("'", "&apos;")
    )
