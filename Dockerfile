# Multi-stage Dockerfile for React + FastAPI deployment
# Stage 1: Build React frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build React app
RUN npm run build

# Stage 2: Python backend with built frontend
FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY src/ ./src/
COPY config/ ./config/
COPY backend/ ./backend/
COPY app/ ./app/
COPY .env.example .env

# Ensure __init__.py files exist for Python modules
RUN touch src/__init__.py src/data/__init__.py src/core/__init__.py \
    src/ai/__init__.py src/visualization/__init__.py src/database/__init__.py \
    config/__init__.py backend/__init__.py backend/api/__init__.py

# Copy built React frontend from stage 1
COPY --from=frontend-builder /app/frontend/dist ./backend/static

# Create necessary directories
RUN mkdir -p data/cache data/chromadb data/raw

# Expose port (HuggingFace uses 7860)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/api/health || exit 1

# Run FastAPI backend (serves React frontend + API)
CMD ["uvicorn", "backend.api.main:app", \
     "--host", "0.0.0.0", \
     "--port", "7860"]
