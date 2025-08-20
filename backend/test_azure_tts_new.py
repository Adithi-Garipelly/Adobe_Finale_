#!/usr/bin/env python3
"""
Test script to verify new Azure TTS credentials
"""

import os
import azure.cognitiveservices.speech as speechsdk

# Test with your new credentials
AZURE_TTS_KEY = "29kJSeXw6VeXDiGJbRVf8U9d5fUBiXKI2XJhsKk5QRn4qMP5j4yvJQQJ99BHACGhslBXJ3w3AAAYACOG1bYR"
AZURE_TTS_REGION = "centralindia"
AZURE_TTS_ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"

def test_azure_tts():
    """Test Azure TTS with new credentials"""
    try:
        print("🔑 Testing Azure TTS with new credentials...")
        print(f"Key: {AZURE_TTS_KEY[:20]}...{AZURE_TTS_KEY[-20:]}")
        print(f"Region: {AZURE_TTS_REGION}")
        print(f"Endpoint: {AZURE_TTS_ENDPOINT}")
        
        # Create speech config
        speech_config = speechsdk.SpeechConfig(
            subscription=AZURE_TTS_KEY, 
            region=AZURE_TTS_REGION
        )
        speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
        
        # Test with a simple text
        test_text = "Hello, this is a test of Azure Text to Speech service."
        print(f"\n📝 Test text: {test_text}")
        
        # Create audio output
        output_file = "test_output_new.wav"
        audio_config = speechsdk.audio.AudioOutputConfig(filename=output_file)
        
        # Create synthesizer
        synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config, 
            audio_config=audio_config
        )
        
        print("🎙️ Synthesizing speech...")
        result = synthesizer.speak_text_async(test_text).get()
        
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("✅ Azure TTS SUCCESS!")
            print(f"📁 Audio saved to: {output_file}")
            
            # Check file size
            if os.path.exists(output_file):
                size = os.path.getsize(output_file)
                print(f"📊 File size: {size} bytes")
                if size > 1000:
                    print("🎉 Audio file is properly generated!")
                else:
                    print("⚠️ Audio file is too small, may be corrupted")
            else:
                print("❌ Audio file not found")
                
        else:
            print(f"❌ Azure TTS failed: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"   Reason: {cancellation_details.reason}")
                print(f"   Error details: {cancellation_details.error_details}")
                
    except Exception as e:
        print(f"❌ Error testing Azure TTS: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_azure_tts()
