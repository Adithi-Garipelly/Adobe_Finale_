#!/bin/bash
set -e  # stop on error

# Go to project root (where this script is)
cd "$(dirname "$0")"

echo "🔧 Setting up Adobe Finale project..."

# -------------------------
# Backend Setup
# -------------------------
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt

echo "🚀 Starting backend on http://0.0.0.0:8000 ..."
# Use the correct module path from project root
cd ..
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend health check
echo "⏳ Waiting for backend to be ready..."
for i in {1..20}; do
    if curl -s http://127.0.0.1:8000/health > /dev/null; then
        echo "✅ Backend is running!"
        break
    fi
    sleep 2
done

# -------------------------
# Frontend Setup
# -------------------------
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

echo "🚀 Starting frontend on http://localhost:3000 ..."
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend health check
echo "⏳ Waiting for frontend to be ready..."
for i in {1..20}; do
    if curl -s http://127.0.0.1:3000 > /dev/null; then
        echo "✅ Frontend is running!"
        break
    fi
    sleep 2
done

# -------------------------
# Summary
# -------------------------
echo ""
echo "🎉 All systems go!"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo ""
echo "Press CTRL+C to stop both."

# Kill both when user exits
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
