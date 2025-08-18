#!/bin/bash

# Frontend startup script for Document Insight & Engagement System
echo "🎨 Starting React Frontend..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend is not running on port 8000"
    echo "💡 Please start the backend first with: ./scripts/run_backend.sh"
    exit 1
fi

echo "✅ Backend is running and healthy"

# Set environment variables
export REACT_APP_API_BASE_URL="http://localhost:8000"
export REACT_APP_BACKEND_URL="http://localhost:8000"
export REACT_APP_ADOBE_EMBED_API_KEY="1d691dca47814a4d847ab3286df17a8e"

echo "🔑 Adobe Embed API configured"
echo "🌐 Backend URL: $REACT_APP_BACKEND_URL"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    npm install
fi

# Start the development server
echo "🚀 Starting React development server on port 3000..."
echo "🌐 Frontend: http://localhost:3000"
echo "📱 Backend API: http://localhost:8000"

npm start
