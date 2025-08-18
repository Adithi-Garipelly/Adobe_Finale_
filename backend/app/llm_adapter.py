import os
from typing import Optional
import google.generativeai as genai

# Requires GOOGLE_APPLICATION_CREDENTIALS to be mounted to /credentials/<...>.json
# and env vars: LLM_PROVIDER=gemini, GEMINI_MODEL=gemini-2.5-flash

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

def _ensure_client():
    # The SDK reads GOOGLE_APPLICATION_CREDENTIALS automatically
    genai.configure()  # no args needed if env is present

def gemini_complete(system_prompt: str, user_prompt: str) -> str:
    _ensure_client()
    model = genai.GenerativeModel(GEMINI_MODEL, system_instruction=system_prompt)
    resp = model.generate_content(user_prompt, safety_settings=None)  # keep defaults if needed
    if hasattr(resp, "text"):
        return resp.text
    # Concatenate parts if needed
    return "\n".join([p.text for p in getattr(resp, "candidates", []) if getattr(p, "text", "")])
