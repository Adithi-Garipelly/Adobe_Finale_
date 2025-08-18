#!/bin/bash

# 🎨 Frontend Startup Script for Document Insight & Engagement System
# This script sets up the environment and starts the React development server

set -e  # Exit on any error

echo "🎨 Starting Document Insight & Engagement System Frontend..."
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "📍 Project root: $PROJECT_ROOT"
echo "📍 Frontend directory: $FRONTEND_DIR"

# Check if we're in the right directory
if [ ! -f "$FRONTEND_DIR/package.json" ]; then
    echo "❌ Error: package.json not found in $FRONTEND_DIR"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "⚠️  Warning: Backend is not running on http://localhost:8000"
    echo "   Please start the backend first using: ./scripts/run_backend.sh"
    echo "   Or start it manually and ensure it's running on port 8000"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Frontend startup cancelled"
        exit 1
    fi
else
    echo "✅ Backend is running and healthy"
fi

# Set environment variables
export REACT_APP_API_BASE_URL="http://localhost:8000"
export REACT_APP_BACKEND_URL="http://localhost:8000"

# Check for Adobe Embed API key
if [ -z "$REACT_APP_ADOBE_EMBED_API_KEY" ]; then
    echo "⚠️  Warning: REACT_APP_ADOBE_EMBED_API_KEY not set"
    echo "   PDF viewing will use fallback PDF.js instead of Adobe Embed API"
    echo "   To enable Adobe Embed API, set:"
    echo "   export REACT_APP_ADOBE_EMBED_API_KEY='your_key_here'"
    echo ""
else
    echo "✅ Adobe Embed API key configured"
fi

echo "📋 Environment Configuration:"
echo "   REACT_APP_API_BASE_URL: $REACT_APP_API_BASE_URL"
echo "   REACT_APP_BACKEND_URL: $REACT_APP_BACKEND_URL"
echo "   REACT_APP_ADOBE_EMBED_API_KEY: ${REACT_APP_ADOBE_EMBED_API_KEY:-Not set}"

# Check if node_modules exists
if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd "$FRONTEND_DIR"
    npm install
else
    echo "✅ Node.js dependencies already installed"
fi

# Check if dependencies are properly installed
echo "🔍 Verifying dependencies..."
cd "$FRONTEND_DIR"
if npm list react react-dom > /dev/null 2>&1; then
    echo "✅ Core React dependencies verified"
else
    echo "❌ React dependencies missing, reinstalling..."
    npm install
fi

# Start the development server
echo "🚀 Starting React development server..."
echo "   URL: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo ""

cd "$FRONTEND_DIR"
npm start
