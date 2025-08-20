#!/bin/bash

echo "🚀 Starting Adobe Finale Application..."

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null
pkill -f "npm start" 2>/dev/null

# Wait for processes to stop
sleep 2

# Start backend
echo "🔧 Starting Backend on Port 8080..."
cd backend
source .venv/bin/activate
export PYTHONPATH=$PWD
nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 > ../backend.log 2>&1 &
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Test backend
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8080"
else
    echo "❌ Backend failed to start. Check backend.log"
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend on Port 3000..."
cd frontend
nohup npm start > ../frontend.log 2>&1 &
cd ..

echo "🎉 Application starting!"
echo "🌐 Backend: http://localhost:8080"
echo "🎨 Frontend: http://localhost:3000"
echo "📊 Health: http://localhost:8080/health"
echo ""
echo "📝 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🔄 To restart everything: ./start_everything.sh"
