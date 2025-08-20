#!/bin/bash

# 🎯 Adobe Finale - Quick Start Script for Judges
# This script automatically sets up and starts your Adobe Finale application

echo "🚀 Adobe Finale - Quick Start for Judges"
echo "=========================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the Adobe_Round3 directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
if [[ "$PYTHON_VERSION" < "3.10" ]]; then
    echo "❌ Python version $PYTHON_VERSION is too old. Please install Python 3.10+"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+"
    exit 1
fi

NODE_VERSION=$(node --version | cut -d. -f1 | tr -d 'v')
if [[ "$NODE_VERSION" -lt 16 ]]; then
    echo "❌ Node.js version $(node --version) is too old. Please install Node.js 16+"
    exit 1
fi

echo "✅ Node.js $(node --version) found"

# Check npm
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm"
    exit 1
fi

echo "✅ npm $(npm --version) found"

echo ""
echo "🚀 Starting Adobe Finale..."

# Start Backend
echo "🔧 Starting Backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies if requirements.txt is newer than .venv
if [ requirements.txt -nt .venv ]; then
    echo "📥 Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start backend in background
echo "🚀 Starting backend server on port 8080..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8080 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8080"
else
    echo "❌ Backend failed to start. Check backend.log for details"
    exit 1
fi

# Start Frontend
echo "🎨 Starting Frontend..."
cd ../frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📥 Installing Node.js dependencies..."
    npm install
fi

# Start frontend in background
echo "🚀 Starting frontend on port 3000..."
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 10

# Check if frontend is running
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start. Check frontend.log for details"
    exit 1
fi

echo ""
echo "🎉 Adobe Finale is now running!"
echo "================================="
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend:  http://localhost:8080"
echo "📚 API Docs: http://localhost:8080/docs"
echo ""
echo "📖 Demo Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Upload 2-3 PDF research papers"
echo "3. Select text and generate insights"
echo "4. Create and play podcasts"
echo ""
echo "🛑 To stop the application:"
echo "   Backend:  kill $BACKEND_PID"
echo "   Frontend: kill $FRONTEND_PID"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend/backend.log"
echo "   Frontend: tail -f frontend/frontend.log"
echo ""
echo "🎯 Happy judging! 🚀"
