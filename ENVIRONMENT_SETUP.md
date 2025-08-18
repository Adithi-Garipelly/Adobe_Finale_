# 🔑 Environment Setup Guide

This guide will help you set up all the required API keys for the Document Insight & Engagement System.

## 📋 Required API Keys

### 1. Adobe PDF Embed API Key ✅ (Already Set)
- **Status**: ✅ Configured
- **Key**: `1d691dca47814a4d847ab3286df17a8e`
- **Location**: `frontend/.env`
- **Purpose**: PDF viewing with Adobe Embed API

### 2. Google Gemini API Key 🔑 (Need to Set)
- **Status**: ❌ Not configured
- **Purpose**: AI-powered Q&A and insights generation
- **Model**: Gemini 2.5 Flash

#### How to Get Gemini API Key:
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with your Google account
3. Click "Get API key" or "Create API key"
4. Copy the generated key

#### Set Gemini API Key:
```bash
# Add to your environment variables
export GOOGLE_APPLICATION_CREDENTIALS="your-gemini-key-here"
export GEMINI_API_KEY="your-gemini-key-here"
```

### 3. Azure Speech Services Key 🔑 (Need to Set)
- **Status**: ❌ Not configured
- **Purpose**: Text-to-speech for podcast and chat answers
- **Features**: Neural voices, multiple languages

#### How to Get Azure Speech Key:
1. Go to [Azure Portal](https://portal.azure.com/)
2. Create a new "Speech Service" resource
3. Go to "Keys and Endpoint" section
4. Copy Key 1 and Region

#### Set Azure Speech Keys:
```bash
# Add to your environment variables
export AZURE_TTS_KEY="your-azure-speech-key-here"
export AZURE_TTS_REGION="your-azure-region-here"
export AZURE_TTS_ENDPOINT="https://your-region.tts.speech.microsoft.com"
```

## 🚀 Complete Environment Setup

### Option 1: Environment Variables (Recommended)
```bash
# Backend environment variables
export GOOGLE_APPLICATION_CREDENTIALS="your-gemini-key"
export GEMINI_API_KEY="your-gemini-key"
export AZURE_TTS_KEY="your-azure-speech-key"
export AZURE_TTS_REGION="eastus"
export AZURE_TTS_ENDPOINT="https://eastus.tts.speech.microsoft.com"

# Frontend environment variables (already set)
# REACT_APP_API=http://localhost:8000
# REACT_APP_ADOBE_EMBED_API_KEY=1d691dca47814a4d847ab3286df17a8e
```

### Option 2: Create .env Files

#### Backend (.env)
```env
GOOGLE_APPLICATION_CREDENTIALS=your-gemini-key
GEMINI_API_KEY=your-gemini-key
AZURE_TTS_KEY=your-azure-speech-key
AZURE_TTS_REGION=eastus
AZURE_TTS_ENDPOINT=https://eastus.tts.speech.microsoft.com
```

#### Frontend (.env) - Already Created ✅
```env
REACT_APP_API=http://localhost:8000
REACT_APP_ADOBE_EMBED_API_KEY=1d691dca47814a4d847ab3286df17a8e
```

## 🧪 Test Your Setup

### 1. Test Gemini Integration
```bash
# Backend should start without errors
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Test Azure TTS
```bash
# Check if TTS endpoints are available
curl -X POST "http://localhost:8000/chat/speak" \
  -F "text=Hello, this is a test of Azure TTS"
```

### 3. Test Frontend
```bash
# Frontend should load without errors
cd frontend
npm start
```

## 🔍 Troubleshooting

### Gemini API Issues
- **Error**: "Failed to initialize Gemini"
- **Solution**: Check `GOOGLE_APPLICATION_CREDENTIALS` environment variable
- **Verify**: Key is valid and has proper permissions

### Azure TTS Issues
- **Error**: "Azure TTS failed"
- **Solution**: Check `AZURE_TTS_KEY` and `AZURE_TTS_REGION`
- **Verify**: Speech service is active in Azure portal

### Adobe PDF Issues
- **Error**: "Failed to initialize PDF viewer"
- **Solution**: Check `REACT_APP_ADOBE_EMBED_API_KEY` in frontend/.env
- **Verify**: Key is valid and domain is whitelisted

## 📱 What You Get After Setup

1. **✅ PDF Upload & Viewing**: Adobe Embed API
2. **✅ AI Chat**: Ask questions about PDFs with Gemini
3. **✅ Voice Answers**: Hear responses with Azure TTS
4. **✅ Semantic Search**: Find related content across PDFs
5. **✅ AI Insights**: Generate structured analysis
6. **✅ Podcast Generation**: Create audio content from text

## 🎯 Next Steps

1. **Get Gemini API Key** from Google AI Studio
2. **Get Azure Speech Key** from Azure Portal
3. **Set environment variables** or create .env files
4. **Test the system** with all features enabled
5. **Enjoy your AI-powered PDF analysis system!** 🚀

## 💡 Pro Tips

- **Free Tiers**: Both Gemini and Azure offer free tiers
- **Rate Limits**: Be aware of API rate limits for production use
- **Security**: Never commit API keys to version control
- **Backup**: Keep your API keys in a secure location

Need help? Check the console logs and ensure all environment variables are properly set! 🛠️
