#!/usr/bin/env python3
"""
Test script for full integration: Gemini LLM + Azure TTS
"""

import os
from app.universal_insights import UniversalInsightsGenerator

def test_full_integration():
    """Test the complete system integration"""
    
    # Set Azure credentials
    os.environ['AZURE_SPEECH_KEY'] = 'JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv'
    os.environ['AZURE_SPEECH_REGION'] = 'centralindia'
    
    print("🧠 Testing Full System Integration...")
    print("=" * 60)
    
    # Sample search results (simulating FAISS search)
    sample_search_results = [
        {
            "document_name": "A Comprehensive Survey on Transfer Learning (1).pdf",
            "page_number": 1,
            "content": "Transfer learning aims at improving the performance of target learners on target domains by transferring the knowledge contained in different but related source domains.",
            "score": 0.95
        },
        {
            "document_name": "Transfer learning handbook.pdf", 
            "page_number": 1,
            "content": "Transfer learning is the improvement of learning in a new task through the transfer of knowledge from a related task that has already been learned.",
            "score": 0.92
        },
        {
            "document_name": "A_comprehensive_survey_of_federated_transfer_learn (1).pdf",
            "page_number": 4,
            "content": "Given an/some observation(s) corresponding to m source domain(s) and task(s)... transfer learning aims to utilize the knowledge implied in the source domain(s) to improve the performance of the learned decision functions... on the target domain(s).",
            "score": 0.88
        }
    ]
    
    # Sample selected text
    selected_text = "Transfer learning is a machine learning technique where a model trained on one task is repurposed on a second related task."
    
    print("📚 Sample Documents:")
    for i, doc in enumerate(sample_search_results, 1):
        print(f"  {i}. {doc['document_name']} (Page {doc['page_number']})")
        print(f"     Content: {doc['content'][:80]}...")
        print(f"     Score: {doc['score']:.3f}")
        print()
    
    print(f"🔍 Selected Text: {selected_text}")
    print()
    
    try:
        # Create generator and test
        generator = UniversalInsightsGenerator()
        
        print("🚀 Generating comprehensive insights...")
        result = generator.generate_insights(selected_text, sample_search_results)
        
        print("✅ Insights generated successfully!")
        print(f"📅 Generated at: {result.get('generated_at', 'N/A')}")
        print()
        
        # Display relevant sections
        print("📚 Relevant Sections:")
        print("-" * 40)
        for i, section in enumerate(result.get('relevant_sections', []), 1):
            print(f"{i}. {section['document_name']}")
            print(f"   Page {section['page_number']} ({section['section_type']})")
            print(f"   Content: {section['content'][:100]}...")
            print(f"   Score: {section['relevance_score']:.3f}")
            print()
        
        # Display insights
        print("🧠 Insights:")
        print("-" * 40)
        insights = result.get('insights', {})
        for key, value in insights.items():
            print(f"• {key.replace('_', ' ').title()}:")
            print(f"  {value[:150]}...")
            print()
        
        # Display podcast info
        print("🎧 Podcast Generation:")
        print("-" * 40)
        transcript = result.get('podcast_transcript', '')
        print(f"📝 Transcript Length: {len(transcript)} characters")
        print(f"📖 Preview: {transcript[:200]}...")
        print()
        
        # Check audio generation
        podcast_audio = result.get('podcast_audio')
        if podcast_audio:
            print("🎵 Audio Generated Successfully!")
            print(f"   📁 File: {podcast_audio.get('filename', 'N/A')}")
            print(f"   📊 Size: {podcast_audio.get('file_size', 'N/A')} bytes")
            print(f"   ⏱️ Duration: {podcast_audio.get('duration_estimate', 'N/A')}")
            print(f"   🎤 Voice: {podcast_audio.get('voice_used', 'N/A')}")
            print(f"   📍 Region: {podcast_audio.get('region', 'N/A')}")
        else:
            print("⚠️ Audio generation failed or not attempted")
        
        print("\n🎉 Full integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_full_integration()
