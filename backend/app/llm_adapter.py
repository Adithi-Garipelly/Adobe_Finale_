import os
from typing import Optional
import google.generativeai as genai

# Use GEMINI_API_KEY environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def _ensure_client():
    # Configure Gemini with API key
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY environment variable not set")
    genai.configure(api_key=GEMINI_API_KEY)

def gemini_complete(system_prompt: str, user_prompt: str) -> str:
    _ensure_client()
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
    resp = model.generate_content(user_prompt, safety_settings=None)  # keep defaults if needed
    if hasattr(resp, "text"):
        return resp.text
    # Concatenate parts if needed
    return "\n".join([p.text for p in getattr(resp, "candidates", []) if getattr(p, "text", "")])
