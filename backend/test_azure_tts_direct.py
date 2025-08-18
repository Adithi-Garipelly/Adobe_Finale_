#!/usr/bin/env python3
"""
Test Azure TTS directly to diagnose any issues
"""
import os
from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

# Load environment variables
load_dotenv()

def test_azure_tts():
    """Test Azure TTS with your credentials"""
    
    # Get credentials
    key = os.getenv("AZURE_TTS_KEY")
    region = os.getenv("AZURE_TTS_REGION")
    endpoint = os.getenv("AZURE_TTS_ENDPOINT")
    
    print(f"Testing Azure TTS...")
    print(f"Key: {key[:20] if key else 'Not set'}...")
    print(f"Region: {region}")
    print(f"Endpoint: {endpoint}")
    
    if not key or not region:
        print("❌ Missing Azure credentials")
        return False
    
    try:
        # Try different configurations
        configs = [
            {"name": "Region-based", "config": speechsdk.SpeechConfig(subscription=key, region=region)},
            {"name": "Endpoint-based", "config": speechsdk.SpeechConfig(subscription=key, endpoint=endpoint) if endpoint else None}
        ]
        
        for config_info in configs:
            if config_info["config"] is None:
                continue
                
            print(f"\n🔧 Testing {config_info['name']} configuration...")
            
            speech_config = config_info["config"]
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            # Test with a simple text
            test_text = "Hello, this is a test of Azure Text to Speech."
            
            # Create audio config
            audio_config = speechsdk.audio.AudioOutputConfig(filename=f"test_output_{config_info['name'].lower()}.mp3")
            
            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config, 
                audio_config=audio_config
            )
            
            print(f"🎵 Synthesizing: '{test_text}'")
            
            # Synthesize speech
            result = synthesizer.speak_text_async(test_text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                print(f"✅ {config_info['name']} Azure TTS successful! Audio file created: test_output_{config_info['name'].lower()}.mp3")
                return True
            else:
                print(f"❌ {config_info['name']} Azure TTS failed: {result.reason}")
                if hasattr(result, 'cancellation_details'):
                    print(f"   Details: {result.cancellation_details.reason}")
                    if hasattr(result.cancellation_details, 'error_details'):
                        print(f"   Error: {result.cancellation_details.error_details}")
        
        return False
            
    except Exception as e:
        print(f"❌ Error testing Azure TTS: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_azure_tts()
    if success:
        print("\n🎉 Azure TTS is working correctly!")
    else:
        print("\n💥 Azure TTS test failed. Check your credentials and region.")
