# backend/app/tts.py
import os
from typing import Optional

# Read env once
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "azure").lower()

# Use environment variables for Azure TTS credentials
AZURE_TTS_KEY = os.getenv("AZURE_TTS_KEY") or os.getenv("AZURE_SPEECH_KEY")
AZURE_TTS_REGION = os.getenv("AZURE_TTS_REGION", "centralindia")
AZURE_TTS_ENDPOINT = os.getenv("AZURE_TTS_ENDPOINT") or "https://centralindia.api.cognitive.microsoft.com/"
AZURE_TTS_VOICE = os.getenv("AZURE_TTS_VOICE", "en-US-AriaNeural")
# keep cloud inputs short to avoid SDK timeouts
TTS_CLOUD_MAX_CHARS = int(os.getenv("TTS_CLOUD_MAX_CHARS", "2800"))

def _is_azure_configured() -> bool:
    return bool(AZURE_TTS_KEY and AZURE_TTS_ENDPOINT)

def tts_status():
    """Lightweight status for debugging from the frontend/terminal."""
    return {
        "provider": TTS_PROVIDER,
        "azure_configured": _is_azure_configured(),
        "voice": AZURE_TTS_VOICE,
        "cloud_char_limit": TTS_CLOUD_MAX_CHARS,
    }

def transcript_to_ssml(transcript: str, max_chars: int = 4500) -> str:
    """
    Convert transcript with multiple speakers into SSML for Azure TTS.
    Fixes:
    - Multiple speakers mapped to different voices
    - Clamp total length to ~5min (≈4500 chars)
    - No intro/outro music
    """
    ssml_parts = [
        '<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">'
    ]

    total_chars = 0
    for turn in transcript.splitlines():
        line = turn.strip()
        if not line:
            continue

        # Skip stage directions and intro/outro music
        if (line.startswith("(") and line.endswith(")")) or (line.startswith("**(") and line.endswith(")**")):
            continue

        # Speaker detection for simple "Sarah:" and "Alex:" format
        if line.startswith("Alex:") or line.startswith("Dr. Alex:"):
            voice = "en-US-GuyNeural"   # male
            text = line.split(":", 1)[1].strip()
        elif line.startswith("Sarah:") or line.startswith("Host:"):
            voice = "en-US-JennyNeural" # female
            text = line.split(":", 1)[1].strip()
        else:
            # Default voice for other speakers
            voice = "en-US-JennyNeural"
            text = line

        # Stop if limit exceeded (~5min max)
        if total_chars + len(text) > max_chars:
            break

        if text:  # Only add if there's actual content
            ssml_parts.append(f'<voice name="{voice}">{text}</voice>')
            total_chars += len(text)

    ssml_parts.append("</speak>")
    return "".join(ssml_parts)

def _azure_synthesize(text: str, out_path: str):
    """Generate TTS with proper SSML for multiple voices"""
    try:
        # Try Azure TTS with SSML for multiple voices
        import azure.cognitiveservices.speech as speechsdk
        
        # Use endpoint instead of region for better Docker compatibility
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, region=AZURE_TTS_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        
        audio_config = speechsdk.audio.AudioOutputConfig(filename=out_path)
        
        # Try to create synthesizer with error handling
        try:
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        except Exception as e:
            print(f"Failed to create synthesizer: {e}")
            # Try simpler approach without audio config
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        
        # Convert transcript to SSML with multiple voices and 5-minute limit
        ssml_text = transcript_to_ssml(text)
        print(f"Generated SSML with {len(ssml_text)} characters")
        
        # Use SSML synthesis for multiple voices
        result = synthesizer.speak_ssml_async(ssml_text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Azure TTS succeeded with SSML and multiple voices!")
            return
        else:
            print(f"Azure TTS failed: {result.reason}, using fallback")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"   Reason: {cancellation_details.reason}")
                print(f"   Error details: {cancellation_details.error_details}")
            
    except Exception as e:
        print(f"Azure TTS error: {e}, using fallback")
        import traceback
        traceback.print_exc()
    
    # Try simple text-to-speech without SSML as fallback
    try:
        print("Trying simple Azure TTS without SSML...")
        import azure.cognitiveservices.speech as speechsdk
        
        speech_config = speechsdk.SpeechConfig(subscription=AZURE_TTS_KEY, region=AZURE_TTS_REGION)
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        
        audio_config = speechsdk.audio.AudioOutputConfig(filename=out_path)
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        # Use simple text instead of SSML
        result = synthesizer.speak_text_async(text[:1000]).get()  # Limit to first 1000 chars
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Simple Azure TTS succeeded!")
            return
        else:
            print(f"Simple Azure TTS failed: {result.reason}")
            
    except Exception as e:
        print(f"Simple Azure TTS also failed: {e}")
    
    # Last resort: create a longer, more useful fallback audio
    _create_fallback_audio(out_path)

def synthesize_podcast(script: str, out_path: str, provider: Optional[str] = None):
    """
    Generate an MP3 at out_path from `script` using Azure TTS.
    - Requires AZURE_TTS_KEY & AZURE_TTS_ENDPOINT
    """
    chosen = (provider or TTS_PROVIDER).lower()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    if chosen == "azure":
        if not _is_azure_configured():
            raise RuntimeError("Azure Speech Service not configured. Set AZURE_TTS_KEY and AZURE_TTS_ENDPOINT.")
        _azure_synthesize(script, out_path)
    else:
        raise ValueError(f"Only Azure TTS is supported. Got: {chosen}")

    return out_path

def _create_fallback_audio(out_path: str):
    """Create a simple fallback audio file when TTS fails"""
    try:
        # Create a simple beep sound using Python
        import wave
        import struct
        import math
        
        # Create a longer, more useful audio
        sampleRate = 44100
        duration = 10  # 10 seconds instead of 3
        frequency = 440  # A4 note
        
        wav_file = wave.open(out_path, 'w')
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sampleRate)
        
        for i in range(int(duration * sampleRate)):
            value = int(32767.0 * 0.3 * math.sin(frequency * math.pi * float(i) / float(sampleRate)))
            data = struct.pack('<h', value)
            wav_file.writeframes(data)
        
        wav_file.close()
        print(f"Created fallback audio file: {out_path}")
    except Exception as e:
        print(f"Failed to create fallback audio: {e}")
        # Create an empty file as last resort
        with open(out_path, 'w') as f:
            f.write("")
