#!/usr/bin/env python3
"""
Test script for Azure TTS integration
"""

import os
from app.tts_adapter import generate_podcast_audio

def test_azure_tts():
    """Test Azure TTS with sample transcript"""
    
    # Set Azure credentials (using the keys you provided)
    os.environ['AZURE_SPEECH_KEY'] = 'JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv'
    os.environ['AZURE_SPEECH_REGION'] = 'centralindia'
    os.environ['AZURE_SPEECH_ENDPOINT'] = 'https://centralindia.api.cognitive.microsoft.com/'
    
    print("🎵 Testing Azure TTS Integration...")
    print("=" * 50)
    
    # Sample podcast transcript
    sample_transcript = """(Intro Music: Upbeat, tech-focused melody fades in and out)

Host: Hey, and welcome to our quick dive into a fascinating topic that's all over your reading list: Transfer Learning. You just selected a paragraph about it from a paper on building load forecasting, and let's connect the dots from a few other studies you've read.

Host: At its core, every document you have defines transfer learning in a similar way: using knowledge gained from one task to get better and faster at a new, related task. Think of it like this: mastering a foundational skill, then applying it to a new, but similar challenge.

Host: So, from a simple definition to a practical application, and then to a major challenge and a futuristic extension, that one paragraph you selected is a gateway to a whole network of ideas in your library. Keep exploring!

(Outro Music: Upbeat melody fades out)"""
    
    try:
        print("🎤 Generating podcast audio...")
        print(f"📝 Transcript length: {len(sample_transcript)} characters")
        
        # Generate audio
        result = generate_podcast_audio(sample_transcript, "test_podcast.mp3")
        
        if result and result.get('status') == 'success':
            print("✅ Podcast audio generated successfully!")
            print(f"📁 File: {result.get('filename')}")
            print(f"📊 Size: {result.get('file_size')} bytes")
            print(f"⏱️ Duration: {result.get('duration_estimate')}")
            print(f"🎤 Voice: {result.get('voice_used')}")
            print(f"📍 Region: {result.get('region')}")
        else:
            print("❌ Podcast audio generation failed")
            print(f"Result: {result}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_azure_tts()
