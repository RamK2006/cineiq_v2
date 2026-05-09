#!/bin/bash

# CINEIQ Setup Script
# This script automates the complete setup process

set -e  # Exit on error

echo "🎬 CINEIQ Setup Script"
echo "======================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}❌ Python 3 is required but not installed.${NC}" >&2; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}❌ Node.js is required but not installed.${NC}" >&2; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker is required but not installed.${NC}" >&2; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose is required but not installed.${NC}" >&2; exit 1; }

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
if (( $(echo "$PYTHON_VERSION < 3.11" | bc -l) )); then
    echo -e "${RED}❌ Python 3.11+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# Check Node version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if (( NODE_VERSION < 20 )); then
    echo -e "${RED}❌ Node.js 20+ required (found v$NODE_VERSION)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Version requirements met${NC}"
echo ""

# Environment setup
echo "🔧 Setting up environment..."

if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  .env file not found. Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env and add your API keys before continuing.${NC}"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

echo -e "${GREEN}✅ Environment configured${NC}"
echo ""

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..
echo -e "${GREEN}✅ Backend dependencies installed${NC}"
echo ""

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo -e "${GREEN}✅ Frontend dependencies installed${NC}"
echo ""

# Start Docker services
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis qdrant
echo "⏳ Waiting for services to be ready..."
sleep 10
echo -e "${GREEN}✅ Docker services started${NC}"
echo ""

# Run database migrations
echo "🗄️  Running database migrations..."
cd backend
alembic upgrade head
cd ..
echo -e "${GREEN}✅ Database migrations complete${NC}"
echo ""

# Download MovieLens data
echo "📥 Downloading MovieLens 25M dataset..."
if [ ! -d "data/ml-25m" ]; then
    python data_pipeline/download_movielens.py
    echo -e "${GREEN}✅ MovieLens dataset downloaded${NC}"
else
    echo -e "${YELLOW}⚠️  MovieLens dataset already exists, skipping...${NC}"
fi
echo ""

# Ingest TMDB data
echo "🎬 Ingesting TMDB movie data..."
read -p "Do you want to ingest TMDB data? (requires TMDB API key) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python data_pipeline/ingest_tmdb.py
    echo -e "${GREEN}✅ TMDB data ingested${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping TMDB ingestion${NC}"
fi
echo ""

# Train ML models
echo "🧠 Training ML models..."
read -p "Do you want to train ML models? (may take 15-30 minutes) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Training SVD model..."
    python backend/app/ml/train_svd.py
    echo ""
    echo "Training NCF model..."
    python backend/app/ml/train_ncf.py
    echo -e "${GREEN}✅ ML models trained${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping model training${NC}"
fi
echo ""

# Generate embeddings
echo "🎨 Generating vector embeddings..."
read -p "Do you want to generate embeddings? (requires trained models) [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python data_pipeline/generate_embeddings.py
    echo -e "${GREEN}✅ Embeddings generated${NC}"
else
    echo -e "${YELLOW}⚠️  Skipping embedding generation${NC}"
fi
echo ""

# Final summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Start all services: ${GREEN}make dev${NC}"
echo "2. Access frontend: ${GREEN}http://localhost:3000${NC}"
echo "3. Access backend API: ${GREEN}http://localhost:8000${NC}"
echo "4. Access API docs: ${GREEN}http://localhost:8000/docs${NC}"
echo "5. Access Grafana: ${GREEN}http://localhost:3001${NC} (admin/admin)"
echo ""
echo "For production deployment, see: ${GREEN}DEPLOYMENT.md${NC}"
echo ""
echo "Happy coding! 🚀"
