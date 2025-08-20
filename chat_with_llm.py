#!/usr/bin/env python3
"""
Sample script for LLM calls - Required by Hackathon Constraints
"""
from backend.app.llm_adapter import gemini_complete

def chat_with_llm(prompt):
    """Chat with LLM using Gemini"""
    try:
        response = gemini_complete(
            system_prompt="You are a helpful AI assistant for the Adobe Hackathon project.",
            user_prompt=prompt
        )
        return response
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    prompt = "Hello! Summarize Adobe Hackathon."
    response = chat_with_llm(prompt)
    print(response)
