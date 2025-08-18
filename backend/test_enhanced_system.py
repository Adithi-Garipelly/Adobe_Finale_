#!/usr/bin/env python3
"""
Comprehensive test script for the enhanced Document Insight & Engagement System
"""

import os
import sys
import time
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

def test_semantic_index():
    """Test the enhanced semantic index"""
    print("🧠 Testing Enhanced Semantic Index...")
    print("=" * 50)
    
    try:
        from semantic import SemanticIndex
        
        # Create index
        index = SemanticIndex()
        print("✅ SemanticIndex created successfully")
        
        # Test stats
        stats = index.get_stats()
        print(f"📊 Initial stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ Semantic index test failed: {e}")
        return False

def test_llm_adapter():
    """Test the enhanced LLM adapter"""
    print("\n🤖 Testing Enhanced LLM Adapter...")
    print("=" * 50)
    
    try:
        from llm_adapter import generate_insights, get_llm_status
        
        # Test LLM status
        status = get_llm_status()
        print(f"📋 LLM Status: {status}")
        
        # Test fallback insights
        sample_text = "Transfer learning is a machine learning technique."
        sample_related = [
            {
                "doc_name": "test.pdf",
                "heading": "Introduction",
                "snippet": "Transfer learning improves performance.",
                "score": 0.9
            }
        ]
        
        insights = generate_insights(sample_text, sample_related)
        print(f"💡 Generated insights: {insights[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM adapter test failed: {e}")
        return False

def test_tts_adapter():
    """Test the enhanced TTS adapter"""
    print("\n🎵 Testing Enhanced TTS Adapter...")
    print("=" * 50)
    
    try:
        from tts_adapter import (
            get_tts_status, get_available_voices,
            format_transcript_for_single_speaker
        )
        
        # Test TTS status
        status = get_tts_status()
        print(f"📋 TTS Status: {status}")
        
        # Test available voices
        voices = get_available_voices()
        print(f"🎤 Available voices: {list(voices['single_speaker'].keys())}")
        
        # Test transcript formatting
        sample_text = "This is a test selection."
        sample_related = [{"doc_name": "test.pdf", "heading": "Test"}]
        sample_insights = "This is a test insight."
        
        transcript = format_transcript_for_single_speaker(
            sample_text, sample_related, sample_insights
        )
        print(f"📝 Transcript preview: {transcript[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ TTS adapter test failed: {e}")
        return False

def test_indexer():
    """Test the enhanced indexer"""
    print("\n📚 Testing Enhanced Indexer...")
    print("=" * 50)
    
    try:
        from indexer import get_index_status
        
        # Test index status
        status = get_index_status()
        print(f"📊 Index Status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Indexer test failed: {e}")
        return False

def test_main_app():
    """Test the main FastAPI app imports"""
    print("\n🚀 Testing Main FastAPI App...")
    print("=" * 50)
    
    try:
        from main import app
        
        print("✅ FastAPI app imported successfully")
        print(f"📋 App title: {app.title}")
        print(f"📋 App version: {app.version}")
        
        # Test route registration
        routes = [route.path for route in app.routes]
        print(f"🛣️  Registered routes: {len(routes)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Main app test failed: {e}")
        return False

def test_environment():
    """Test environment configuration"""
    print("\n⚙️  Testing Environment Configuration...")
    print("=" * 50)
    
    try:
        # Check required environment variables
        env_vars = {
            "DATA_DIR": os.environ.get("DATA_DIR", "Not set"),
            "LLM_PROVIDER": os.environ.get("LLM_PROVIDER", "Not set"),
            "AZURE_TTS_KEY": os.environ.get("AZURE_TTS_KEY", "Not set"),
            "AZURE_TTS_REGION": os.environ.get("AZURE_TTS_REGION", "Not set")
        }
        
        print("📋 Environment Variables:")
        for key, value in env_vars.items():
            if "KEY" in key and value != "Not set":
                masked_value = value[:10] + "..." if len(value) > 10 else value
                print(f"   {key}: {masked_value}")
            else:
                print(f"   {key}: {value}")
        
        # Check data directories
        data_dir = os.environ.get("DATA_DIR", os.path.join(os.getcwd(), "data"))
        required_dirs = ["uploads", "index", "audio"]
        
        print("\n📁 Data Directories:")
        for subdir in required_dirs:
            dir_path = os.path.join(data_dir, subdir)
            if os.path.exists(dir_path):
                print(f"   ✅ {subdir}: {dir_path}")
            else:
                print(f"   ❌ {subdir}: {dir_path} (missing)")
        
        return True
        
    except Exception as e:
        print(f"❌ Environment test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Enhanced System Test Suite")
    print("=" * 60)
    print(f"⏰ Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests = [
        ("Environment Configuration", test_environment),
        ("Semantic Index", test_semantic_index),
        ("LLM Adapter", test_llm_adapter),
        ("TTS Adapter", test_tts_adapter),
        ("Indexer", test_indexer),
        ("Main FastAPI App", test_main_app)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready for competition!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
