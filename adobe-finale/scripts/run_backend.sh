#!/bin/bash

# Backend startup script for Document Insight & Engagement System
echo "🚀 Starting FastAPI Backend..."

# Navigate to backend directory
cd "$(dirname "$0")/../backend"

# Set environment variables
export DATA_DIR="$(pwd)/../data"
export AZURE_TTS_KEY="JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Optional LLM configuration
export LLM_PROVIDER="gemini"
export GEMINI_MODEL="gemini-2.0-flash-exp"
export OPENAI_MODEL="gpt-4o-mini"

# Create data directories
mkdir -p "$DATA_DIR/uploads"
mkdir -p "$DATA_DIR/index"
mkdir -p "$DATA_DIR/audio"

echo "📁 Data directory: $DATA_DIR"
echo "🔑 Azure TTS configured"
echo "🧠 LLM Provider: $LLM_PROVIDER"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source .venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start the backend server
echo "🚀 Starting Uvicorn server on port 8000..."
echo "📊 Health check: http://localhost:8000/health"
echo "📚 API docs: http://localhost:8000/docs"

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
