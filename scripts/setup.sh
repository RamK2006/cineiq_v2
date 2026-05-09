#!/bin/bash

echo "🎬 CINEIQ Setup Script"
echo "======================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "   Please copy .env.example to .env and add your API keys"
    echo "   Required keys: TMDB_API_KEY, GROQ_API_KEY, CLERK_SECRET_KEY"
    exit 1
fi

# Check for required API keys
source .env

if [ "$TMDB_API_KEY" == "REPLACE_WITH_YOUR_KEY" ]; then
    echo "❌ Error: TMDB_API_KEY not set in .env"
    echo "   Get your API key from: https://www.themoviedb.org/settings/api"
    exit 1
fi

echo "✅ Environment configured"
echo ""

# Step 1: Download MovieLens data
echo "📥 Step 1/5: Downloading MovieLens 25M dataset..."
python data_pipeline/download_movielens.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to download MovieLens data"
    exit 1
fi
echo ""

# Step 2: Start databases
echo "🗄️  Step 2/5: Starting databases (PostgreSQL, Redis, Qdrant)..."
docker-compose up -d postgres redis qdrant
sleep 10
echo ""

# Step 3: Run migrations
echo "🔄 Step 3/5: Running database migrations..."
cd backend && alembic upgrade head && cd ..
if [ $? -ne 0 ]; then
    echo "❌ Failed to run migrations"
    exit 1
fi
echo ""

# Step 4: Ingest TMDB data
echo "🎥 Step 4/5: Ingesting TMDB movie data..."
python data_pipeline/ingest_tmdb.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to ingest TMDB data"
    exit 1
fi
echo ""

# Step 5: Train ML models
echo "🧠 Step 5/5: Training ML models (this may take 10-30 minutes)..."
python backend/app/ml/train_svd.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to train SVD model"
    exit 1
fi

python backend/app/ml/train_ncf.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to train NCF model"
    exit 1
fi
echo ""

# Step 6: Generate embeddings
echo "🎨 Step 6/5: Generating vector embeddings..."
python data_pipeline/generate_embeddings.py
if [ $? -ne 0 ]; then
    echo "❌ Failed to generate embeddings"
    exit 1
fi
echo ""

echo "✨ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "   1. Run 'make dev' to start all services"
echo "   2. Open http://localhost:3000 for the frontend"
echo "   3. Open http://localhost:8000/docs for API documentation"
echo ""
echo "📊 Monitoring:"
echo "   - Grafana: http://localhost:3001 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo ""
