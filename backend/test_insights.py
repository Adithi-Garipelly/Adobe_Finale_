#!/usr/bin/env python3
"""
Test script for UniversalInsightsGenerator
"""

from app.universal_insights import UniversalInsightsGenerator

def test_insights_generation():
    """Test the insights generation with sample data"""
    
    # Sample search results (simulating what we'd get from FAISS search)
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
    
    # Create generator and test
    generator = UniversalInsightsGenerator()
    
    print("🧠 Testing UniversalInsightsGenerator...")
    print("=" * 50)
    
    try:
        # Generate insights
        result = generator.generate_insights(selected_text, sample_search_results)
        
        print("✅ Insights generated successfully!")
        print(f"📅 Generated at: {result.get('generated_at', 'N/A')}")
        print()
        
        # Display relevant sections
        print("📚 Relevant Sections:")
        print("-" * 30)
        for i, section in enumerate(result.get('relevant_sections', []), 1):
            print(f"{i}. {section['document_name']}")
            print(f"   Page {section['page_number']} ({section['section_type']})")
            print(f"   Content: {section['content'][:100]}...")
            print(f"   Score: {section['relevance_score']:.3f}")
            print()
        
        # Display insights
        print("🧠 Insights:")
        print("-" * 30)
        insights = result.get('insights', {})
        for key, value in insights.items():
            print(f"• {key.replace('_', ' ').title()}:")
            print(f"  {value[:100]}...")
            print()
        
        # Display podcast transcript
        print("🎧 Podcast Transcript:")
        print("-" * 30)
        transcript = result.get('podcast_transcript', '')
        print(transcript[:200] + "..." if len(transcript) > 200 else transcript)
        
        print("\n✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_insights_generation()
