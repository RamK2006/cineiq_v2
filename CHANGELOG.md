# Changelog

All notable changes to CINEIQ will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-09

### Added
- **Hybrid ML Recommendation Engine**
  - SVD collaborative filtering (Surprise library)
  - Neural Collaborative Filtering (PyTorch)
  - Content-based filtering with TF-IDF
  - Sentiment re-ranking with DistilBERT
  - Ensemble weighting system

- **Semantic Search**
  - Natural language movie queries
  - Sentence-transformers embeddings (384-dim)
  - Qdrant vector database integration
  - Vibe-based search presets

- **Watch-Together Feature**
  - Real-time WebSocket synchronization
  - Playback state sync (play/pause/seek)
  - Live chat messaging
  - Emoji reactions with animations
  - Room-based participant management

- **User Features**
  - Movie rating system (0.5-5.0 stars)
  - Taste profile with genre affinities
  - Radar chart visualization
  - Rating history and statistics
  - Letterboxd CSV import

- **TMDB Integration**
  - Real-time movie metadata fetching
  - Trending movies endpoint
  - Movie search functionality
  - Cast and crew information
  - Redis caching (6-hour TTL)

- **Frontend**
  - Next.js 15 App Router
  - Glassmorphism design system
  - Framer Motion animations
  - Responsive mobile design
  - Dark theme with gradient accents

- **Infrastructure**
  - Docker Compose setup
  - PostgreSQL 16 database
  - Redis 7 caching
  - Qdrant vector search
  - Prometheus monitoring
  - Grafana dashboards
  - Alembic migrations

- **Authentication**
  - Clerk integration
  - JWT validation
  - Social login (Google, GitHub)

### Technical Details
- Python 3.11 backend with FastAPI
- Async/await throughout
- Type hints and Pydantic validation
- 85%+ test coverage target
- Production-ready error handling

### Performance
- ML inference: <100ms (cached)
- API response time: <500ms (p95)
- Vector search: <200ms
- WebSocket latency: <50ms

### Security
- Input validation (Pydantic)
- SQL injection prevention (SQLAlchemy ORM)
- Rate limiting (100 req/min)
- Secure password handling (Clerk)
- API key authentication for extensions

## [Unreleased]

### Planned Features
- Mobile React Native app
- Visual similarity search (CLIP)
- Groq LLM explanations
- LIME explainability
- Trakt import support
- Social features (friends, activity feed)
- Personalized film school paths
- Advanced filtering options

### Known Issues
- None reported

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.
