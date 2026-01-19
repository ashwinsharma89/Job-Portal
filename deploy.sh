#!/bin/bash

# Agentic Job Platform - Deployment Script
# Usage: ./deploy.sh [build]

echo "🚀 Starting Deployment for Agentic Job Platform..."

# 1. Check for Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed."
    exit 1
fi

# 2. Setup Directories
mkdir -p backend/chroma_db
mkdir -p backend/data

# 3. Create .env if missing (Template)
if [ ! -f .env ]; then
    echo "Creating .env template..."
    echo "DATABASE_URL=sqlite+aiosqlite:///./jobplatform.db" > .env
    echo "CHROMA_PERSIST_DIR=./chroma_db" >> .env
fi

# 4. Build and Run
if [ "$1" == "build" ]; then
    echo "🏗️  Rebuilding Containers..."
    docker-compose up -d --build
else
    echo "▶️  Starting Containers..."
    docker-compose up -d
fi

# 5. Check Status
sleep 5
echo "📊 Service Status:"
docker-compose ps

echo "✅ Deployment Scripts Executed."
echo "   - Frontend: http://localhost:80"
echo "   - Backend:  http://localhost:8000"
