#!/bin/bash

echo "🚀 Starting Document Insight & Engagement System..."
echo "=================================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Set environment variables
export DATA_DIR="$(pwd)/data"
export AZURE_TTS_KEY="JNhLVS1WDukjZ8iGPc4AMVs5rf6ueEB1DmM4l42HoyfEu3wZXTSSJQQJ99BHACGhslBXJ3w3AAAYACOGBWMv"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Create data directories
mkdir -p data/uploads data/index data/audio

echo "📁 Data directories created"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd backend
if [ ! -d ".venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt > /dev/null 2>&1

echo "🚀 Starting FastAPI backend on port 8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 10

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend
npm install > /dev/null 2>&1

echo "🚀 Starting React frontend on port 3000..."
npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 15

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check frontend.log for details."
    exit 1
fi

echo ""
echo "🎉 System is now running!"
echo "=================================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🏥 Health Check: http://localhost:8000/health"
echo ""
echo "💡 How to use:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Upload PDF files in the Upload PDFs tab"
echo "3. View PDFs in the PDF Viewer tab"
echo "4. Generate insights by selecting text"
echo "5. View results in the AI Insights tab"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user to stop
wait
