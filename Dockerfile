# ---------- Frontend Build Stage ----------
FROM node:18-alpine AS frontend-build
WORKDIR /fe
COPY frontend/package*.json ./
RUN npm ci --only=production
COPY frontend/ ./
# Supply your Adobe Embed API key at build time or bake .env
# ARG REACT_APP_ADOBE_EMBED_API_KEY
# ENV REACT_APP_ADOBE_EMBED_API_KEY=${REACT_APP_ADOBE_EMBED_API_KEY}
RUN npm run build

# ---------- Backend Stage ----------
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app

# System dependencies for PDF processing and ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend application
COPY backend/app ./app

# Copy built frontend
COPY --from=frontend-build /fe/build ./static

# Create data directories
RUN mkdir -p /app/data/uploads /app/data/index /app/data/audio
ENV DATA_DIR=/app/data

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
