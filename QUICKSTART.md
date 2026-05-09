# CINEIQ Quick Start Guide

Get CINEIQ running in 5 minutes!

## Prerequisites

- Python 3.11+
- Node.js 20+
- Docker & Docker Compose
- Git

## Step 1: Clone & Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/iitg-coding-club/cineiq.git
cd cineiq

# Copy environment file
cp .env.example .env
```

## Step 2: Get API Keys (3 minutes)

Edit `.env` and add these keys:

### Required Keys:

1. **Clerk** (Authentication) - https://clerk.com
   - Sign up for free
   - Create an application
   - Copy `CLERK_SECRET_KEY` and `CLERK_PUBLISHABLE_KEY`

2. **TMDB** (Movie Data) - https://www.themoviedb.org/settings/api
   - Sign up for free
   - Request API key
   - Copy `TMDB_API_KEY`

3. **Groq** (LLM) - https://console.groq.com
   - Sign up for free
   - Generate API key
   - Copy `GROQ_API_KEY`

## Step 3: Run Setup (Automated)

### Option A: Using Make (Recommended)

```bash
# One command to rule them all
make setup
```

This will:
- Download MovieLens 25M dataset
- Train ML models (SVD + NCF)
- Ingest TMDB movie data
- Generate vector embeddings
- Run database migrations

### Option B: Manual Setup

```bash
# Download data
python data_pipeline/download_movielens.py

# Start databases
docker-compose up -d postgres redis qdrant

# Run migrations
cd backend && alembic upgrade head && cd ..

# Train models
python backend/app/ml/train_svd.py
python backend/app/ml/train_ncf.py

# Ingest TMDB data
python data_pipeline/ingest_tmdb.py

# Generate embeddings
python data_pipeline/generate_embeddings.py
```

## Step 4: Start the Application

```bash
# Start all services
make dev

# Or manually
docker-compose up
```

## Step 5: Access the Application

Open your browser:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3001 (admin/admin)

## What's Next?

### Explore Features:

1. **Search Movies**
   - Try semantic search: "dark psychological thriller"
   - Use vibe presets: "Mind-Bending", "Feel-Good"

2. **Rate Movies**
   - Click on any movie
   - Rate it with stars
   - Get personalized recommendations

3. **Watch Together**
   - Create a watch room
   - Share the link with friends
   - Sync playback in real-time

4. **Import Ratings**
   - Go to Profile
   - Upload Letterboxd CSV
   - Get instant recommendations

### Development:

```bash
# Run tests
make test

# Lint code
make lint

# View logs
docker-compose logs -f backend
```

## Troubleshooting

### Backend won't start?

```bash
# Check logs
docker-compose logs backend

# Common fix: Restart services
docker-compose restart
```

### ML models not found?

```bash
# Train models
make train
```

### Database connection error?

```bash
# Restart PostgreSQL
docker-compose restart postgres

# Check if running
docker-compose ps
```

### Frontend build fails?

```bash
cd frontend
rm -rf .next node_modules
npm install
npm run dev
```

## Need Help?

- 📖 Full docs: [README.md](README.md)
- 🚀 Deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- 🐛 Issues: https://github.com/iitg-coding-club/cineiq/issues
- 💬 Discussions: https://github.com/iitg-coding-club/cineiq/discussions

## Quick Commands Reference

```bash
# Development
make dev              # Start all services
make dev-build        # Rebuild and start
make test             # Run tests
make lint             # Lint code

# Data & Models
make download-data    # Download MovieLens
make train            # Train ML models
make build-embeddings # Generate embeddings

# Database
make migrate          # Run migrations

# Cleanup
make clean            # Stop and remove everything
```

## Performance Tips

- First startup takes 5-10 minutes (model training)
- Subsequent startups: ~30 seconds
- ML inference: <100ms (cached)
- API response: <500ms average

## What You Get

✅ Hybrid ML recommendation engine  
✅ Semantic movie search  
✅ Real-time watch-together  
✅ User taste profiles  
✅ Letterboxd import  
✅ Beautiful glassmorphism UI  
✅ Production-ready infrastructure  

Enjoy CINEIQ! 🎬✨
