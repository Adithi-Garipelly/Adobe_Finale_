#!/bin/bash

echo "🚀 Starting Document Insight & Engagement System with Adobe PDF Embed API"
echo "=================================================================="

# Check prerequisites
echo "🔍 Checking prerequisites..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed"
    exit 1
fi

echo "✅ All prerequisites met"

# Create data directories
echo "📁 Creating data directories..."
mkdir -p backend/data/uploads backend/data/audio backend/data/index

# Set environment variables
export DATA_DIR="$(pwd)/backend/data"
export AZURE_TTS_KEY="your-azure-tts-key"
export AZURE_TTS_REGION="centralindia"
export AZURE_TTS_ENDPOINT="https://centralindia.api.cognitive.microsoft.com/"

# Check for Adobe API key
if [ ! -f "frontend/.env" ]; then
    echo ""
    echo "⚠️  ADOBE PDF EMBED API SETUP REQUIRED!"
    echo "======================================"
    echo "1. Get your FREE API key from: https://www.adobe.com/go/dcsdks_credentials"
    echo "2. Create frontend/.env file with:"
    echo "   REACT_APP_ADOBE_EMBED_API_KEY=your-actual-client-id-here"
    echo "3. Restart this script"
    echo ""
    echo "For detailed setup, see: frontend/ADOBE_SETUP.md"
    echo ""
    
    # Create .env template
    cat > frontend/.env.template << EOF
# Adobe PDF Embed API Key
# Get your free key from: https://www.adobe.com/go/dcsdks_credentials
REACT_APP_ADOBE_EMBED_API_KEY=your-actual-client-id-here

# Backend API URL
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_BACKEND_URL=http://localhost:8000
EOF
    
    echo "📝 Created frontend/.env.template - copy to frontend/.env and add your key"
    exit 1
fi

# Check if Adobe key is set
if grep -q "your-actual-client-id-here" frontend/.env; then
    echo ""
    echo "⚠️  Please update frontend/.env with your actual Adobe API key"
    echo "   Current: REACT_APP_ADOBE_EMBED_API_KEY=your-actual-client-id-here"
    echo "   Should be: REACT_APP_ADOBE_EMBED_API_KEY=abc123def456..."
    echo ""
    exit 1
fi

echo "✅ Adobe PDF Embed API configured"

# Start backend
echo "🐍 Starting Python backend..."
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "⚛️  Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "🎉 System is running successfully!"
echo "=================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "📖 Features:"
echo "   ✅ Professional Adobe PDF viewing"
echo "   ✅ Text selection for insights"
echo "   ✅ AI-powered analysis"
echo "   ✅ Podcast generation"
echo "   ✅ Multi-PDF management"
echo ""
echo "🎯 Next steps:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Upload a PDF file"
echo "   3. Select text to generate insights"
echo "   4. Generate podcasts from insights"
echo ""
echo "Press Ctrl+C to stop all services"

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
