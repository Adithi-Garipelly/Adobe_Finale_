#!/usr/bin/env python3
"""Test podcast generation"""

import os
from dotenv import load_dotenv
from app.tts import synthesize_podcast

# Load environment variables
load_dotenv()

def test_podcast_generation():
    """Test the actual podcast generation function"""
    
    print("🎙️ Testing Podcast Generation")
    print("=" * 40)
    
    # Test script similar to what the app generates
    test_script = """Sarah (Host): Welcome to Research Insights, where we dive deep into the latest academic discoveries! I'm Sarah, and today we're exploring a fascinating concept from your research.

Dr. Alex (Co-host): Hi everyone! I'm Dr. Alex, and I'm excited to break down this concept across multiple research papers. What we found is absolutely fascinating!

Sarah: Absolutely! So, we're looking at the concept from your selected text, and Dr. Alex, what are the key findings across these documents?

Dr. Alex: Great question! Based on your document library, we've discovered some incredible connections. The concept appears in multiple contexts, each adding a unique perspective to our understanding."""

    print(f"📝 Test Script Length: {len(test_script)} characters")
    print(f"📄 Script Preview: {test_script[:100]}...")
    print()
    
    try:
        print("🔄 Generating podcast...")
        output_path = "test_podcast.mp3"
        
        # Call the actual function
        result = synthesize_podcast(
            script=test_script,
            out_path=output_path,
            provider="azure"
        )
        
        print(f"✅ Podcast generated successfully!")
        print(f"📁 Output file: {output_path}")
        print(f"📊 File size: {os.path.getsize(output_path) if os.path.exists(output_path) else 'File not found'} bytes")
        
        return True
        
    except Exception as e:
        print(f"❌ Podcast generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_podcast_generation()
    
    print()
    if success:
        print("🎉 Podcast generation test passed!")
    else:
        print("❌ Podcast generation test failed.")
