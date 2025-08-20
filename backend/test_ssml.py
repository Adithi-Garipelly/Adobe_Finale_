#!/usr/bin/env python3
"""
Test script for the universal SSML wrapper
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from tts import transcript_to_ssml

# Test transcript (similar to what you showed)
test_transcript = """**(Intro Music fades in and out)**

**Sarah (Host):** Welcome back to "Decode It," the podcast where we break down complex research into fascinating, digestible insights! Today, we're diving into the heart of a developer's headache: runtime errors.

**Dr. Alex (Co-host):** Absolutely, Sarah! It's like being a detective, piecing together clues from a system that isn't quite working as expected.

**(Outro Music fades in)**
"""

print("🎙️ Testing Universal SSML Wrapper")
print("=" * 50)
print("\n📝 Input Transcript:")
print(test_transcript)
print("\n🔧 Generated SSML:")
print("=" * 50)
ssml_output = transcript_to_ssml(test_transcript)
print(ssml_output)
print("\n✅ SSML Conversion Complete!")
