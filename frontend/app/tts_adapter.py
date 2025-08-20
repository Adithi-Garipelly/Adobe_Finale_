# backend/app/tts_adapter.py
import os
import uuid
import logging
from typing import Tuple, Dict, Any, Optional
from pathlib import Path
import azure.cognitiveservices.speech as speechsdk

logger = logging.getLogger(__name__)

AZURE_KEY = os.environ.get("AZURE_TTS_KEY", "JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv")
AZURE_ENDPOINT = os.environ.get("AZURE_TTS_ENDPOINT", "https://centralindia.api.cognitive.microsoft.com/")
AZURE_REGION = os.environ.get("AZURE_TTS_REGION", "centralindia")
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
AUDIO_DIR = os.path.join(DATA_DIR, "audio")

os.makedirs(AUDIO_DIR, exist_ok=True)

VOICES = {
    "single_speaker": {
        "en-US-JennyNeural": "Natural female voice (default)",
        "en-US-GuyNeural": "Natural male voice",
        "en-US-AriaNeural": "Professional female voice",
        "en-US-DavisNeural": "Professional male voice"
    },
    "two_speaker": {
        "en-US-JennyNeural": "Host (female)",
        "en-US-GuyNeural": "Co-host (male)",
        "en-US-AriaNeural": "Expert (female)",
        "en-US-DavisNeural": "Expert (male)"
    }
}

def synthesize_podcast(text: str, voice: str = "en-US-JennyNeural", 
                      filename: Optional[str] = None) -> Tuple[str, str]:
    """
    Synthesize podcast audio using Azure TTS
    
    Returns:
        Tuple of (mp3_path, transcript_path)
    """
    try:
        import azure.cognitiveservices.speech as speechsdk
        
        if not AZURE_KEY or AZURE_KEY == "JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv":
            logger.warning("⚠️ Using default Azure TTS key - set AZURE_TTS_KEY for production")
        
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_KEY, 
            region=AZURE_REGION
        )
        
        speech_config.speech_synthesis_voice_name = voice
        speech_config.speech_synthesis_speaking_rate = 0.9
        speech_config.speech_synthesis_pitch = 0
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        
        if not filename:
            file_id = uuid.uuid4().hex
            filename = f"podcast_{file_id}"
        
        mp3_path = os.path.join(AUDIO_DIR, f"{filename}.mp3")
        transcript_path = os.path.join(AUDIO_DIR, f"{filename}.txt")
        
        audio_config = speechsdk.audio.AudioOutputConfig(filename=mp3_path)
        
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        logger.info(f"🎵 Generating podcast audio: {filename}")
        logger.info(f"🎤 Voice: {voice}")
        logger.info(f"📝 Text length: {len(text)} characters")
        
        result = synthesizer.speak_text_async(text).get()
        
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            error_msg = f"TTS failed: {result.reason}"
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                error_msg += f" - {cancellation_details.reason}"
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    error_msg += f" - {cancellation_details.error_details}"
            
            logger.error(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        if not os.path.exists(mp3_path):
            raise RuntimeError("Audio file was not created")
        
        if not os.path.exists(transcript_path):
            raise RuntimeError("Transcript file was not created")
        
        mp3_size = os.path.getsize(mp3_path)
        transcript_size = os.path.getsize(transcript_path)
        
        logger.info(f"✅ Podcast generated successfully!")
        logger.info(f"   📁 MP3: {mp3_path} ({mp3_size} bytes)")
        logger.info(f"   📄 Transcript: {transcript_path} ({transcript_size} bytes)")
        
        return mp3_path, transcript_path
        
    except ImportError:
        logger.error("azure-cognitiveservices-speech not installed")
        raise RuntimeError("Azure TTS package not available")
    except Exception as e:
        logger.error(f"❌ Error synthesizing podcast: {e}")
        raise

def format_transcript_for_single_speaker(selected_text: str, related: list, insights: str) -> str:
    """Format transcript for single speaker podcast"""
    try:
        intro = "(Intro Music: Upbeat, tech-focused melody fades in and out)\n\n"
        intro += "Host: Hey, and welcome to our quick dive into a fascinating topic that's all over your reading list! "
        intro += "You just selected some text, and let's connect the dots from your research library.\n\n"
        
        # Parse insights to create structured podcast content
        insight_sections = {}
        current_section = ""
        current_content = []
        
        for line in insights.split('\n'):
            line = line.strip()
            if line.startswith('Definition & Core Principle:'):
                current_section = 'definition'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Application & Context:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'application'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Contradictory Viewpoints / Challenges:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'challenges'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Model Comparison:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'comparison'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Extension to Other Fields:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'extension'
                current_content = [line.split(':', 1)[1].strip()]
            elif line and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            insight_sections[current_section] = '\n'.join(current_content)
        
        body = [
            "Host: First, here's what you highlighted:",
            f"\"{selected_text.strip()}\"",
            "",
            "Host: Now, let me connect the dots across your library to give you some insights:",
        ]
        
        # Add structured insights in podcast format
        if 'definition' in insight_sections:
            body.append(f"Host: At its core, {insight_sections['definition']}")
        
        if 'application' in insight_sections:
            body.append(f"Host: In practice, {insight_sections['application']}")
        
        if 'challenges' in insight_sections:
            body.append(f"Host: However, there are challenges to consider: {insight_sections['challenges']}")
        
        if 'comparison' in insight_sections:
            body.append(f"Host: When comparing approaches: {insight_sections['comparison']}")
        
        if 'extension' in insight_sections:
            body.append(f"Host: Looking beyond this field: {insight_sections['extension']}")
        
        outro = "\n\nHost: Thanks for listening! That's how your selected text connects to the broader research landscape. "
        outro += "Keep exploring and connecting those dots!\n\n"
        outro += "(Outro Music: Upbeat melody fades out)"
        
        return intro + "\n".join(body) + outro
        
    except Exception as e:
        logger.error(f"Error formatting transcript: {e}")
        return f"Error formatting transcript: {e}"

def format_transcript_for_two_speakers(selected_text: str, related: list, insights: str) -> str:
    """Format transcript for two-speaker podcast (competition feature)"""
    try:
        intro = "(Intro Music: Upbeat, tech-focused melody fades in and out)\n\n"
        intro += "Host: Hey researchers! Welcome to our deep dive into your selected text.\n"
        intro += "Co-host: We're going to explore how this connects to your broader research library.\n\n"
        
        # Parse insights to create structured podcast content (same as single speaker)
        insight_sections = {}
        current_section = ""
        current_content = []
        
        for line in insights.split('\n'):
            line = line.strip()
            if line.startswith('Definition & Core Principle:'):
                current_section = 'definition'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Application & Context:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'application'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Contradictory Viewpoints / Challenges:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'challenges'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Model Comparison:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'comparison'
                current_content = [line.split(':', 1)[1].strip()]
            elif line.startswith('Extension to Other Fields:'):
                if current_section:
                    insight_sections[current_section] = '\n'.join(current_content)
                current_section = 'extension'
                current_content = [line.split(':', 1)[1].strip()]
            elif line and current_section:
                current_content.append(line)
        
        # Add the last section
        if current_section:
            insight_sections[current_section] = '\n'.join(current_content)
        
        body = [
            "Host: First, let's look at what you highlighted:",
            f"\"{selected_text.strip()}\"",
            "",
            "Co-host: Great selection! Now let me analyze how this connects across your documents:",
        ]
        
        # Add structured insights in podcast format
        if 'definition' in insight_sections:
            body.append(f"Host: At its core, {insight_sections['definition']}")
        
        if 'application' in insight_sections:
            body.append(f"Co-host: In practice, {insight_sections['application']}")
        
        if 'challenges' in insight_sections:
            body.append(f"Host: However, there are challenges to consider: {insight_sections['challenges']}")
        
        if 'comparison' in insight_sections:
            body.append(f"Co-host: When comparing approaches: {insight_sections['comparison']}")
        
        if 'extension' in insight_sections:
            body.append(f"Host: Looking beyond this field: {insight_sections['extension']}")
        
        outro = "\n\nHost: Fascinating connections, right?\n"
        outro += "Co-host: Absolutely! That's the power of connecting insights across your research library.\n"
        outro += "Host: Thanks for listening, and keep exploring those connections!\n\n"
        outro += "(Outro Music: Upbeat melody fades out)"
        
        return intro + "\n".join(body) + outro
        
    except Exception as e:
        logger.error(f"Error formatting two-speaker transcript: {e}")
        return format_transcript_for_single_speaker(selected_text, related, insights)

def generate_podcast_with_transcript(selected_text: str, related: list, insights: str, 
                                   voice: str = "en-US-JennyNeural", 
                                   speaker_mode: str = "single") -> Dict[str, Any]:
    """
    Generate complete podcast with transcript
    
    Args:
        selected_text: User's selected text
        related: Related sections from search
        insights: Generated insights
        voice: TTS voice to use
        speaker_mode: "single" or "two_speaker"
    
    Returns:
        Dict with mp3_url, transcript_url, and metadata
    """
    try:
        # Format transcript based on speaker mode
        if speaker_mode == "two_speaker":
            transcript = format_transcript_for_two_speakers(selected_text, related, insights)
        else:
            transcript = format_transcript_for_single_speaker(selected_text, related, insights)
        
        # Generate unique filename
        file_id = uuid.uuid4().hex
        filename = f"podcast_{file_id}"
        
        # Synthesize audio
        mp3_path, transcript_path = synthesize_podcast(transcript, voice, filename)
        
        # Get file stats
        mp3_size = os.path.getsize(mp3_path)
        transcript_size = os.path.getsize(transcript_path)
        
        # Calculate estimated duration (rough estimate: 150 words per minute)
        word_count = len(transcript.split())
        duration_minutes = word_count / 150
        duration_str = f"{int(duration_minutes)}m {int((duration_minutes % 1) * 60)}s"
        
        return {
            "status": "success",
            "mp3_url": f"/audio/{os.path.basename(mp3_path)}",
            "transcript_url": f"/audio/{os.path.basename(transcript_path)}",
            "filename": filename,
            "voice": voice,
            "speaker_mode": speaker_mode,
            "duration": duration_str,
            "word_count": word_count,
            "mp3_size": mp3_size,
            "transcript_size": transcript_size,
            "created_at": str(uuid.uuid4().hex)
        }
        
    except Exception as e:
        logger.error(f"Error generating podcast: {e}")
        return {
            "status": "error",
            "error": str(e),
            "mp3_url": None,
            "transcript_url": None
        }

def get_available_voices() -> Dict[str, Dict[str, str]]:
    """Get available voices for different use cases"""
    return VOICES

def get_tts_status() -> Dict[str, Any]:
    """Get TTS configuration status"""
    try:
        return {
            "provider": "azure",
            "configured": bool(AZURE_KEY and AZURE_KEY != "JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv"),
            "region": AZURE_REGION,
            "endpoint": AZURE_ENDPOINT,
            "audio_directory": AUDIO_DIR,
            "available_voices": list(VOICES["single_speaker"].keys())
        }
    except Exception as e:
        logger.error(f"Error getting TTS status: {e}")
        return {"error": str(e)}

def synthesize_podcast_simple(text: str, voice: str = "en-US-JennyNeural") -> Tuple[str, str]:
    """Simple podcast synthesis (backward compatibility)"""
    return synthesize_podcast(text, voice)
