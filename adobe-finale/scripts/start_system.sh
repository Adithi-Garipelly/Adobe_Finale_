#!/bin/bash

# Complete system startup script for Document Insight & Engagement System
echo "🚀 Starting Document Insight & Engagement System..."
echo "=================================================="

# Get the project root directory
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Check prerequisites
echo ""
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    echo "💡 Please install Python 3.8+ and try again"
    exit 1
fi
echo "✅ Python 3 found: $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed"
    echo "💡 Please install Node.js 16+ and try again"
    exit 1
fi
echo "✅ Node.js found: $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed"
    echo "💡 Please install npm and try again"
    exit 1
fi
echo "✅ npm found: $(npm --version)"

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
export DATA_DIR="$PROJECT_ROOT/data"
export AZURE_TTS_KEY="JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Frontend environment variables
export REACT_APP_ADOBE_EMBED_API_KEY="1d691dca47814a4d847ab3286df17a8e"
export REACT_APP_API_BASE_URL="http://localhost:8000"
export REACT_APP_BACKEND_URL="http://localhost:8000"

# Optional LLM configuration
export LLM_PROVIDER="gemini"
export GEMINI_MODEL="gemini-2.0-flash-exp"
export OPENAI_MODEL="gpt-4o-mini"

echo "🔑 Azure TTS configured"
echo "🔑 Adobe Embed API configured"
echo "🧠 LLM Provider: $LLM_PROVIDER"

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p "$DATA_DIR/uploads"
mkdir -p "$DATA_DIR/index"
mkdir -p "$DATA_DIR/audio"
echo "✅ Data directories created"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down system..."
    echo "💡 Press Ctrl+C again to force quit"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        echo "🛑 Stopping backend (PID: $BACKEND_PID)..."
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        echo "🛑 Stopping frontend (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    echo "✅ System shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo ""
echo "🚀 Starting backend..."
cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Start backend in background
echo "🚀 Starting Uvicorn server on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to be healthy
echo "⏳ Waiting for backend to be healthy..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy and running on port 8000"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to start within 30 seconds"
        cleanup
        exit 1
    fi
    
    echo "⏳ Waiting... ($i/30)"
    sleep 1
done

# Start frontend
echo ""
echo "🎨 Starting frontend..."
cd "$PROJECT_ROOT/frontend"

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start frontend in background
echo "🚀 Starting React development server on port 3000..."
npm start &
FRONTEND_PID=$!

# Wait for frontend to be ready
echo "⏳ Waiting for frontend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is running on port 3000"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to start within 30 seconds"
        cleanup
        exit 1
    fi
    
    echo "⏳ Waiting... ($i/30)"
    sleep 1
done

# System is ready!
echo ""
echo "🎉 SYSTEM IS READY! 🎉"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3000"
echo "📱 Backend API: http://localhost:8000"
echo "📊 Health Check: http://localhost:8000/health"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 To stop the system, press Ctrl+C"
echo "💡 To view logs, check the terminal output"
echo "💡 To restart services, run this script again"
echo ""

# Wait for user interrupt
wait
