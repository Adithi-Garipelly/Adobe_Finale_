# src/podcast.py
from fastapi import APIRouter, HTTPException
import os
import uuid
import json
from pathlib import Path
from .llm_adapter import gemini_complete
from .tts import synthesize_podcast

router = APIRouter()

OUTPUT_DIR = Path("data/audio")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/generate_podcast")
async def generate_podcast(insights: dict):
    """
    Generate a podcast-style transcript + audio overview using Gemini + Azure TTS.
    """
    try:
        # 1. Create transcript with Gemini LLM
        prompt = f"""
        You are a podcast host. Create a 2–3 min engaging audio transcript based on these insights.
        Make it sound natural, clear, and educational.
        Insights JSON:
        {json.dumps(insights, indent=2)}
        """
        transcript = gemini_complete(
            system_prompt="You are a podcast host creating engaging research content.",
            user_prompt=prompt
        )

        # 2. Convert transcript to audio via Azure TTS
        file_id = str(uuid.uuid4())
        audio_path = OUTPUT_DIR / f"podcast_{file_id}.mp3"
        synthesize_podcast(transcript, str(audio_path))

        return {
            "status": "success",
            "transcript": transcript,
            "audioUrl": f"/files/audio/podcast_{file_id}.mp3"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
