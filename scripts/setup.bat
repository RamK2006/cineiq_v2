@echo off
echo 🎬 CINEIQ Setup Script
echo ======================
echo.

REM Check if .env exists
if not exist .env (
    echo ❌ Error: .env file not found
    echo    Please copy .env.example to .env and add your API keys
    echo    Required keys: TMDB_API_KEY, GROQ_API_KEY, CLERK_SECRET_KEY
    exit /b 1
)

echo ✅ Environment configured
echo.

REM Step 1: Download MovieLens data
echo 📥 Step 1/6: Downloading MovieLens 25M dataset...
python data_pipeline\download_movielens.py
if errorlevel 1 (
    echo ❌ Failed to download MovieLens data
    exit /b 1
)
echo.

REM Step 2: Start databases
echo 🗄️  Step 2/6: Starting databases (PostgreSQL, Redis, Qdrant)...
docker-compose up -d postgres redis qdrant
timeout /t 10 /nobreak > nul
echo.

REM Step 3: Run migrations
echo 🔄 Step 3/6: Running database migrations...
cd backend
alembic upgrade head
cd ..
if errorlevel 1 (
    echo ❌ Failed to run migrations
    exit /b 1
)
echo.

REM Step 4: Ingest TMDB data
echo 🎥 Step 4/6: Ingesting TMDB movie data...
python data_pipeline\ingest_tmdb.py
if errorlevel 1 (
    echo ❌ Failed to ingest TMDB data
    exit /b 1
)
echo.

REM Step 5: Train ML models
echo 🧠 Step 5/6: Training ML models (this may take 10-30 minutes)...
python backend\app\ml\train_svd.py
if errorlevel 1 (
    echo ❌ Failed to train SVD model
    exit /b 1
)

python backend\app\ml\train_ncf.py
if errorlevel 1 (
    echo ❌ Failed to train NCF model
    exit /b 1
)
echo.

REM Step 6: Generate embeddings
echo 🎨 Step 6/6: Generating vector embeddings...
python data_pipeline\generate_embeddings.py
if errorlevel 1 (
    echo ❌ Failed to generate embeddings
    exit /b 1
)
echo.

echo ✨ Setup complete!
echo.
echo 🚀 Next steps:
echo    1. Run 'make dev' or 'docker-compose up' to start all services
echo    2. Open http://localhost:3000 for the frontend
echo    3. Open http://localhost:8000/docs for API documentation
echo.
echo 📊 Monitoring:
echo    - Grafana: http://localhost:3001 (admin/admin)
echo    - Prometheus: http://localhost:9090
echo.
