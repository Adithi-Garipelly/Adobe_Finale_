#!/usr/bin/env python3
"""
Sample script for TTS calls - Required by Hackathon Constraints
"""
from backend.app.tts import synthesize_podcast

def generate_audio(text, output_file):
    """Generate audio using Azure TTS"""
    try:
        synthesize_podcast(
            script=text,
            out_path=output_file,
            provider="azure"
        )
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    text = "Welcome to the Adobe Hackathon Podcast!"
    output_file = "output.mp3"
    success = generate_audio(text, output_file)
    if success:
        print(f"Audio saved at {output_file}")
    else:
        print("Failed to generate audio")
