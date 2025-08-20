# Multi-stage build for frontend and backend
FROM node:18-alpine AS frontend-build
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy backend
COPY backend/ /app/backend/

# Install system dependencies first (🔑 Azure Speech needs these!)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    libssl-dev \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies with retry and timeout
RUN pip install --no-cache-dir --timeout 300 \
    numpy==1.24.3 \
    fastapi==0.111.0 \
    uvicorn[standard]==0.30.3 \
    pdfminer.six==20231228 \
    sentence-transformers==3.0.1 \
    faiss-cpu==1.8.0 \
    google-generativeai==0.7.2 \
    azure-cognitiveservices-speech==1.38.0 \
    python-multipart==0.0.9 \
    pydantic==2.8.2 \
    python-dotenv==1.0.0

# Copy built frontend
COPY --from=frontend-build /fe/build /app/frontend-build

# Expose port 8080
EXPOSE 8080

# Run backend
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8080"]
