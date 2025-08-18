#!/bin/bash

# 🚀 Complete System Startup Script for Document Insight & Engagement System
# This script starts both backend and frontend services

set -e  # Exit on any error

echo "🚀 Starting Document Insight & Engagement System..."
echo "=================================================="
echo "⏰ Started at: $(date)"
echo ""

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "📍 Project root: $PROJECT_ROOT"
echo "📍 Scripts directory: $SCRIPT_DIR"
echo ""

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    
    # Kill backend if running
    if [ -n "$BACKEND_PID" ]; then
        echo "🛑 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # Kill frontend if running
    if [ -n "$FRONTEND_PID" ]; then
        echo "🛑 Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    
    echo "✅ All services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed or not in PATH"
    exit 1
fi

# Check if Node.js is available
if ! command -v node &> /dev/null; then
    echo "❌ Error: Node.js is not installed or not in PATH"
    exit 1
fi

# Check if npm is available
if ! command -v npm &> /dev/null; then
    echo "❌ Error: npm is not installed or not in PATH"
    exit 1
fi

echo "✅ Prerequisites verified"

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
export DATA_DIR="$PROJECT_ROOT/data"
export AZURE_TTS_KEY="JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMV"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Frontend environment variables
export REACT_APP_ADOBE_EMBED_API_KEY="1d691dca47814a4d847ab3286df17a8e"
export REACT_APP_API_BASE_URL="http://localhost:8000"
export REACT_APP_BACKEND_URL="http://localhost:8000"

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

echo "✅ Environment variables set"

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p "$DATA_DIR/uploads" "$DATA_DIR/index" "$DATA_DIR/audio"
echo "✅ Data directories created"

# Start backend
echo ""
echo "🚀 Starting backend service..."
cd "$PROJECT_ROOT"
./scripts/run_backend.sh &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Check if backend is healthy
echo "🏥 Checking backend health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is healthy and responding"
else
    echo "❌ Backend health check failed"
    cleanup
fi

# Start frontend
echo ""
echo "🎨 Starting frontend service..."
cd "$PROJECT_ROOT"
./scripts/run_frontend.sh &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 15

# Check if frontend is responding
echo "🔍 Checking frontend status..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting up..."
fi

# Display system status
echo ""
echo "🎉 System startup completed!"
echo "=================================================="
echo "📊 Service Status:"
echo "   🔧 Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
echo "   🎨 Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo ""
echo "📚 Useful URLs:"
echo "   🏠 Frontend:     http://localhost:3000"
echo "   📖 API Docs:     http://localhost:8000/docs"
echo "   🏥 Health Check: http://localhost:8000/health"
echo "   📊 Status:       http://localhost:8000/status"
echo ""
echo "🔧 Management:"
echo "   📁 Upload PDFs:  http://localhost:3000/upload"
echo "   📚 Documents:    http://localhost:8000/documents"
echo "   🔍 Debug Index:  http://localhost:8000/debug/index"
echo ""
echo "💡 Tips:"
echo "   • Upload PDFs through the frontend interface"
echo "   • Select text in PDFs to generate insights"
echo "   • Generate podcasts from your insights"
echo "   • Check /health for system status"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
