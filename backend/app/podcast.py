# src/podcast.py
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
import os
import uuid
import json
from pathlib import Path
import google.generativeai as genai
import azure.cognitiveservices.speech as speechsdk

router = APIRouter()

# Configure Gemini 2.5 Flash
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
gemini_model = genai.GenerativeModel("gemini-2.5-flash")

# Configure Azure TTS with your region
speech_config = speechsdk.SpeechConfig(
    subscription=os.getenv("AZURE_TTS_KEY"),
    region=os.getenv("AZURE_TTS_REGION")
)
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"

# Get absolute path for audio output directory
UPLOAD_DIR = os.path.abspath(os.getenv("UPLOAD_DIR", "../data/uploads"))
OUTPUT_DIR = Path(UPLOAD_DIR) / "audio"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/generate_podcast")
async def generate_podcast(request: Request):
    """
    Generate a podcast-style transcript + audio overview using Gemini 2.5 Flash + Azure TTS.
    """
    try:
        body = await request.json()
        insights = body.get("insights", {})

        if not insights:
            return JSONResponse({"error": "No insights provided"}, status_code=400)

        # Build podcast script from insights using Gemini 2.5 Flash
        insights_text = ""
        if isinstance(insights, dict):
            # Handle structured insights
            for key, value in insights.items():
                if isinstance(value, str) and value.strip():
                    insights_text += f"- {key}: {value}\n"
        elif isinstance(insights, list):
            # Handle list insights
            insights_text = "\n".join([f"- {i}" for i in insights])
        else:
            insights_text = str(insights)

        prompt = f"""Create a conversational podcast-style script based on these research insights:

{insights_text}

REQUIREMENTS:
- Make it engaging and educational (2-3 minutes)
- Use natural, conversational language
- Structure: Intro → Key Points → Examples → Summary
- End with actionable insights for researchers
- Keep it professional but accessible"""

        gemini_response = gemini_model.generate_content(prompt)
        transcript = gemini_response.text

        # Try to generate audio file with Azure TTS
        audio_filename = f"podcast_{uuid.uuid4().hex}.mp3"
        audio_path = OUTPUT_DIR / audio_filename
        audio_generated = False

        try:
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(audio_path))
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

            speech_synthesis_result = synthesizer.speak_text_async(transcript).get()

            if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                audio_generated = True
                audio_url = f"/files/audio/{audio_filename}"
            else:
                print(f"Azure TTS failed: {speech_synthesis_result.reason}")
                audio_url = None
                
        except Exception as tts_error:
            print(f"Azure TTS error: {tts_error}")
            audio_url = None

        # Return response based on what was generated
        if audio_generated:
            return {
                "status": "success",
                "transcript": transcript,
                "audioUrl": audio_url,
                "audioGenerated": True
            }
        else:
            return {
                "status": "success",
                "transcript": transcript,
                "audioUrl": None,
                "audioGenerated": False,
                "message": "Transcript generated successfully with Gemini 2.5 Flash. Audio generation failed - check Azure TTS credentials."
            }

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
