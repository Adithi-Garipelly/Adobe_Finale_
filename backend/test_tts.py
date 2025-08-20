#!/usr/bin/env python3
"""Test Azure TTS connection"""

import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

def test_azure_tts():
    """Test Azure TTS connection"""
    
    # Get credentials from environment
    key = os.getenv("AZURE_TTS_KEY")
    region = os.getenv("AZURE_TTS_REGION")
    
    print(f"🔑 Testing Azure TTS with:")
    print(f"   Key: {key[:20]}..." if key else "   Key: NOT SET")
    print(f"   Region: {region}")
    print()
    
    if not key or not region:
        print("❌ Missing Azure TTS credentials!")
        return False
    
    try:
        # Test basic connection
        print("🔄 Testing Azure Speech Service connection...")
        
        speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename="test_output.wav")
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
        
        # Test with simple text
        result = synthesizer.speak_text("Hello World")
        
        print(f"✅ TTS Result: {result.reason}")
        
        if result.reason == speechsdk.ResultReason.Canceled:
            print(f"❌ TTS Canceled: {result.cancellation_details.reason}")
            if hasattr(result.cancellation_details, 'error_details'):
                print(f"   Error: {result.cancellation_details.error_details}")
            return False
        elif result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("🎉 TTS Success! Audio file created: test_output.wav")
            return True
        else:
            print(f"⚠️  Unexpected result: {result.reason}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Azure TTS: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Azure TTS Connection Test")
    print("=" * 40)
    
    success = test_azure_tts()
    
    print()
    if success:
        print("✅ Azure TTS is working correctly!")
    else:
        print("❌ Azure TTS test failed. Check credentials and network.")
