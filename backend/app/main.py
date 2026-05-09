from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import redis.asyncio as redis
from qdrant_client import QdrantClient
from .core.config import settings
from .db.session import engine
from .db.models import Base

# Global state
app_state = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting CINEIQ backend...")
    
    # Initialize database
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized")
    
    # Initialize Redis
    app_state["redis"] = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await app_state["redis"].ping()
    print("✅ Redis connected")
    
    # Initialize Qdrant
    app_state["qdrant"] = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    print("✅ Qdrant connected")
    
    # Load embedding service
    try:
        from .services.embedding import EmbeddingService
        app_state["embedding_service"] = EmbeddingService()
        print("✅ Embedding service loaded")
    except Exception as e:
        print(f"⚠️  Embedding service failed to load: {str(e)}")
    
    # Load ML models
    try:
        import pickle
        import os
        if os.path.exists(settings.SVD_MODEL_PATH):
            with open(settings.SVD_MODEL_PATH, 'rb') as f:
                app_state["svd_model"] = pickle.load(f)
            print("✅ SVD model loaded")
        else:
            print("⚠️  SVD model not found (run 'make train')")
    except Exception as e:
        print(f"⚠️  SVD model failed to load: {str(e)}")
    
    print("✨ CINEIQ backend ready!")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down CINEIQ backend...")
    await app_state["redis"].close()
    print("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="CINEIQ API",
    description="Explainable Movie Recommendation Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "cineiq-backend",
        "dependencies": {}
    }
    
    # Check Redis
    try:
        await app_state["redis"].ping()
        health_status["dependencies"]["redis"] = "ok"
    except Exception as e:
        health_status["dependencies"]["redis"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    # Check Qdrant
    try:
        app_state["qdrant"].get_collections()
        health_status["dependencies"]["qdrant"] = "ok"
    except Exception as e:
        health_status["dependencies"]["qdrant"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
    
    return health_status


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to CINEIQ API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Import routers
from .api.v1 import movies, search, recommendations, users, watch_together, imports
app.include_router(movies.router, prefix="/api/v1", tags=["movies"])
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(users.router, prefix="/api/v1", tags=["users"])
app.include_router(watch_together.router, prefix="/api/v1", tags=["watch-together"])
app.include_router(imports.router, prefix="/api/v1", tags=["imports"])
