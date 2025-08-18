#!/bin/bash

# Entrypoint script for Web Application Demo

echo "🚀 Starting Web Application Demo..."

# Set default environment variables if not provided
export NODE_ENV=${NODE_ENV:-"production"}
export API_URL=${API_URL:-"http://localhost:8080"}

# Print configuration
echo "📋 Configuration:"
echo "  - Node Environment: $NODE_ENV"
echo "  - API URL: $API_URL"
echo "  - Port: 8080"

# Create necessary directories
mkdir -p /app/output
mkdir -p /app/uploads

# Set Python path
export PYTHONPATH="/app:/app/src:/app/backend:$PYTHONPATH"

# Start the FastAPI application
echo "🔧 Starting FastAPI backend..."
cd /app

# Run the FastAPI application
exec python -m uvicorn backend.main:app \
    --host 0.0.0.0 \
    --port 8080 \
    --workers 1 \
    --log-level info
