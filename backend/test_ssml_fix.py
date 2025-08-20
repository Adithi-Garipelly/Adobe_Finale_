#!/usr/bin/env python3
"""
Test SSML generation and Azure TTS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.tts import transcript_to_ssml, _azure_synthesize

def test_ssml_generation():
    """Test SSML generation"""
    test_transcript = """Sarah: Welcome back to Deep Dive, the podcast where we unpack the latest breakthroughs in academic research! Today, Alex, we are diving into a field that is not just popular, but truly transformative: Transfer Learning.

Alex: Absolutely, Sarah! It is such a dynamic area. We are looking at a comprehensive survey paper that really tries to connect and systematize the existing research, which is a huge undertaking given how fast this field is moving.

Sarah: That is fascinating! And what about the contradictions or challenges? Research is not always straightforward, right?

Alex: Exactly! We found some fascinating contradictions that actually highlight important research gaps. Different methodologies and contexts lead to varying conclusions."""

    print("🔍 Testing SSML generation...")
    print(f"Input transcript length: {len(test_transcript)} characters")
    
    ssml = transcript_to_ssml(test_transcript)
    print(f"Generated SSML length: {len(ssml)} characters")
    print("\n📝 Generated SSML:")
    print(ssml)
    
    return ssml

def test_azure_tts():
    """Test Azure TTS with the generated SSML"""
    print("\n🎙️ Testing Azure TTS...")
    
    # Test with a simple text first
    test_text = "Hello, this is a test of Azure TTS with SSML."
    
    try:
        _azure_synthesize(test_text, "test_simple.wav")
        print("✅ Simple TTS test completed")
    except Exception as e:
        print(f"❌ Simple TTS test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ssml = test_ssml_generation()
    test_azure_tts()
