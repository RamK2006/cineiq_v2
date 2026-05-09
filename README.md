# 🎬 CINEIQ - Explainable Movie Recommendation Platform



A next-generation movie discovery platform combining hybrid ML recommendation engines (SVD + Neural Collaborative Filtering + Content-Based), semantic search with vector embeddings, and real-time watch-together rooms with WebSocket synchronization.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Node.js 20+
- API Keys (see `.env.example`)

### Setup

1. **Clone and navigate:**
```bash
cd cineiq
```

2. **Configure environment:**
```bash
cp .env.example .env
# Edit .env and add your API keys:
# - CLERK_SECRET_KEY
# - TMDB_API_KEY
# - GROQ_API_KEY
```

3. **One-command setup (downloads data, trains models, builds embeddings):**
```bash
make setup
```

This will:
- Download MovieLens 25M dataset
- Ingest TMDB movie metadata
- Train SVD and NCF models
- Generate Qdrant vector embeddings

4. **Start all services:**
```bash
make dev
```

Services will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Grafana: http://localhost:3001
- Prometheus: http://localhost:9090

## 🏗️ Architecture

### Tech Stack
- **Backend:** FastAPI, Python 3.11, Uvicorn
- **ML:** Surprise (SVD), PyTorch (NCF), sentence-transformers, DistilBERT, CLIP
- **Frontend:** Next.js 15, Framer Motion, TailwindCSS
- **Databases:** PostgreSQL 16, Redis 7, Qdrant
- **Auth:** Clerk
- **APIs:** TMDB v3, Groq (Llama 3.1 70B)

### Key Features
- Hybrid ML recommendation engine (SVD + NCF + Content + Sentiment)
- Semantic "vibe search" with natural language queries
- LIME-powered explainable recommendations
- Real-time Watch-Together with WebSocket sync
- Visual similarity search using CLIP embeddings
- Letterboxd/Trakt import for cold-start

## 📁 Project Structure

```
cineiq/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints
│   │   ├── core/            # Config & security
│   │   ├── db/              # Database models
│   │   ├── ml/              # ML training scripts
│   │   ├── services/        # Business logic
│   │   └── websocket/       # Real-time features
│   ├── alembic/             # DB migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                 # Next.js 15 App Router
│   ├── components/          # React components
│   └── package.json
├── data_pipeline/           # Data ingestion scripts
├── monitoring/              # Grafana dashboards
├── docker-compose.yml
└── Makefile
```

## 🛠️ Development

### Available Commands

```bash
make download-data    # Download MovieLens 25M
make ingest-tmdb      # Fetch TMDB movie data
make train            # Train ML models
make build-embeddings # Generate vector embeddings
make migrate          # Run database migrations
make dev              # Start all services
make test             # Run tests
make lint             # Lint code
make clean            # Clean up everything
```

### API Endpoints

- `POST /api/v1/recommend` - Get personalized recommendations
- `POST /api/v1/search/semantic` - Natural language search
- `GET /api/v1/movies/{id}` - Movie details with AI insights
- `GET /api/v1/movies/trending` - Trending movies
- `POST /api/v1/users/ratings` - Submit rating
- `GET /api/v1/users/profile` - User taste profile
- `POST /api/v1/rooms/create` - Create watch-together room
- `WS /api/v1/ws/room/{id}` - WebSocket for real-time sync

## 🎨 Design System

### Colors
- Base: `#0A0E1A` (near-black with blue undertone)
- Surface: `#111827` (card backgrounds)
- Accent Primary: `#5B5FFF` (interactive elements)
- Accent Violet: `#A78BFA` (secondary highlights)
- Accent Cyan: `#38BDF8` (data highlights)

### Typography
- Display: Inter 700, 48-64px
- Body: Inter 400, 14-16px
- Data/Mono: JetBrains Mono 400, 13-15px

### Animations
- All page transitions: Framer Motion AnimatePresence
- Card hover: scale 1→1.05 with spring physics
- Glassmorphism: backdrop-filter blur(16px)

## 📊 ML Pipeline

### Training Data
- MovieLens 25M (25 million ratings)
- TMDB API (movie metadata, posters, cast)

### Models
1. **SVD (Surprise):** Collaborative filtering, n_factors=100
2. **NCF (PyTorch):** Neural collaborative filtering, embeddings 64-dim
3. **Content-Based:** TF-IDF + sentence-transformers
4. **Sentiment:** DistilBERT re-ranking

### Ensemble Weights
- SVD: 40%
- NCF: 30%
- Content: 20%
- Sentiment: 10%

## 🔐 Environment Variables

See `.env.example` for all required variables:
- `DATABASE_URL` - PostgreSQL connection
- `REDIS_URL` - Redis connection
- `QDRANT_HOST/PORT` - Qdrant vector DB
- `CLERK_SECRET_KEY` - Authentication
- `TMDB_API_KEY` - Movie metadata
- `GROQ_API_KEY` - LLM explanations

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details



## 🙏 Acknowledgments

- [MovieLens](https://grouplens.org/datasets/movielens/) for the dataset
- [TMDB](https://www.themoviedb.org/) for movie metadata
- [Groq](https://groq.com/) for LLM inference
- [Qdrant](https://qdrant.tech/) for vector search
- [Clerk](https://clerk.com/) for authentication


## 🚀 Deployment Status

- **Frontend**: [![Vercel](https://img.shields.io/badge/vercel-deployed-success)](https://cineiq.vercel.app)
- **Backend**: [![Railway](https://img.shields.io/badge/railway-deployed-success)](https://api.cineiq.com)
- **Status**: [![Uptime](https://img.shields.io/badge/uptime-99.9%25-success)](https://status.cineiq.com)




