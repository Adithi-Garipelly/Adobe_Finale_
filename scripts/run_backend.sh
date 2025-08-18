#!/bin/bash

# 🚀 Backend Startup Script for Document Insight & Engagement System
# This script sets up the environment and starts the FastAPI backend

set -e  # Exit on any error

echo "🚀 Starting Document Insight & Engagement System Backend..."
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

echo "📍 Project root: $PROJECT_ROOT"
echo "📍 Backend directory: $BACKEND_DIR"

# Check if we're in the right directory
if [ ! -f "$BACKEND_DIR/requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found in $BACKEND_DIR"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Set environment variables
export DATA_DIR="$PROJECT_ROOT/data"
export AZURE_TTS_KEY="JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Optional LLM configuration
if [ -n "$GEMINI_API_KEY" ]; then
    export LLM_PROVIDER="gemini"
    export GEMINI_MODEL="gemini-2.0-flash-exp"
    echo "✅ Gemini LLM configured"
elif [ -n "$OPENAI_API_KEY" ]; then
    export LLM_PROVIDER="openai"
    export OPENAI_MODEL="gpt-4o-mini"
    echo "✅ OpenAI LLM configured"
else
    echo "ℹ️  No LLM API key set - using fallback insights mode"
fi

echo "📋 Environment Configuration:"
echo "   DATA_DIR: $DATA_DIR"
echo "   AZURE_TTS_REGION: $AZURE_TTS_REGION"
echo "   LLM_PROVIDER: ${LLM_PROVIDER:-none}"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p "$DATA_DIR/uploads" "$DATA_DIR/index" "$DATA_DIR/audio"

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    cd "$BACKEND_DIR"
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source "$BACKEND_DIR/.venv/bin/activate"

# Install/upgrade dependencies
echo "📦 Installing/upgrading dependencies..."
cd "$BACKEND_DIR"
pip install --upgrade pip
pip install -r requirements.txt

# Check if dependencies are properly installed
echo "🔍 Verifying dependencies..."
python -c "import fastapi, uvicorn, faiss, sentence_transformers; print('✅ All core dependencies verified')"

# Health check function
health_check() {
    echo "🏥 Performing health check..."
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is healthy and responding"
        return 0
    else
        echo "❌ Backend health check failed"
        return 1
    fi
}

# Start the server
echo "🚀 Starting FastAPI server..."
echo "   Host: 0.0.0.0"
echo "   Port: 8000"
echo "   API Docs: http://localhost:8000/docs"
echo "   Health: http://localhost:8000/health"
echo ""

# Start server in background
cd "$BACKEND_DIR"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Perform health check
if health_check; then
    echo ""
    echo "🎉 Backend started successfully!"
    echo "=================================================="
    echo "📚 API Documentation: http://localhost:8000/docs"
    echo "🏥 Health Check: http://localhost:8000/health"
    echo "📊 Status: http://localhost:8000/status"
    echo "🔍 Debug Index: http://localhost:8000/debug/index"
    echo ""
    echo "Press Ctrl+C to stop the server"
    
    # Wait for user interrupt
    wait $SERVER_PID
else
    echo "❌ Failed to start backend properly"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi
