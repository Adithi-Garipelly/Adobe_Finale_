#!/bin/bash

echo "🚀 Starting Backend Server on Port 8080..."

# Kill any existing uvicorn processes
pkill -f uvicorn 2>/dev/null

# Wait a moment for processes to stop
sleep 2

# Go to backend directory and start server
cd backend

# Activate virtual environment and start with correct PYTHONPATH
source .venv/bin/activate
export PYTHONPATH=$PWD

# Start the server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

echo "✅ Backend started successfully!"
echo "🌐 Server running at: http://localhost:8080"
echo "📊 Health check: http://localhost:8080/health"
