"""
Generate vector embeddings for Qdrant
"""
import os
import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.db.models import Movie

async def fetch_movies():
    """Fetch all movies from PostgreSQL"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        result = await session.execute(select(Movie))
        movies = result.scalars().all()
    
    await engine.dispose()
    return movies

def create_qdrant_collections(client: QdrantClient):
    """Create Qdrant collections"""
    collections = [
        ("movie_plot_embeddings", 384),  # sentence-transformers dimension
        ("movie_emotional_arc", 512),     # DistilBERT dimension (placeholder)
        ("movie_poster_clip", 512)        # CLIP dimension (placeholder)
    ]
    
    for collection_name, dimension in collections:
        # Check if exists
        try:
            client.get_collection(collection_name)
            print(f"   ✓ Collection '{collection_name}' already exists")
        except:
            # Create collection
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=dimension, distance=Distance.COSINE)
            )
            print(f"   ✓ Created collection '{collection_name}' (dim={dimension})")

def generate_plot_embeddings(movies, model: SentenceTransformer):
    """Generate embeddings for movie plots"""
    print("\n🧠 Generating plot embeddings...")
    
    texts = []
    movie_ids = []
    
    for movie in movies:
        # Combine title, overview, and genres for richer embedding
        text = f"{movie.title}. {movie.overview or ''}"
        if movie.genres:
            text += f" Genres: {', '.join(movie.genres)}"
        
        texts.append(text)
        movie_ids.append(movie.tmdb_id)
    
    # Generate embeddings
    print(f"   Encoding {len(texts)} movie descriptions...")
    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )
    
    return movie_ids, embeddings, movies

def upload_to_qdrant(client: QdrantClient, collection_name: str, movie_ids, embeddings, movies):
    """Upload embeddings to Qdrant"""
    print(f"\n📤 Uploading to Qdrant collection '{collection_name}'...")
    
    points = []
    for idx, (movie_id, embedding, movie) in enumerate(zip(movie_ids, embeddings, movies)):
        point = PointStruct(
            id=idx,
            vector=embedding.tolist(),
            payload={
                "tmdb_id": movie_id,
                "title": movie.title,
                "genres": movie.genres or [],
                "year": movie.release_date[:4] if movie.release_date else None,
                "rating": movie.vote_average,
                "overview": movie.overview or ""
            }
        )
        points.append(point)
    
    # Upload in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i:i+batch_size]
        client.upsert(
            collection_name=collection_name,
            points=batch
        )
        print(f"   Uploaded {min(i+batch_size, len(points))}/{len(points)} points")
    
    print(f"   ✅ Uploaded {len(points)} embeddings")

async def main():
    """Main embedding generation function"""
    print("🎨 Vector Embedding Generation")
    print("=" * 50)
    
    # Initialize Qdrant client
    print(f"\n🔌 Connecting to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}...")
    client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
    
    # Create collections
    print("\n📦 Creating Qdrant collections...")
    create_qdrant_collections(client)
    
    # Load sentence transformer model
    print("\n🤖 Loading sentence-transformers model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("   ✅ Model loaded")
    
    # Fetch movies from database
    print("\n📚 Fetching movies from PostgreSQL...")
    movies = await fetch_movies()
    print(f"   ✅ Fetched {len(movies)} movies")
    
    if len(movies) == 0:
        print("\n❌ No movies found in database!")
        print("   Run 'make ingest-tmdb' first to populate the database")
        return
    
    # Generate and upload plot embeddings
    movie_ids, embeddings, movies_list = generate_plot_embeddings(movies, model)
    upload_to_qdrant(client, "movie_plot_embeddings", movie_ids, embeddings, movies_list)
    
    print("\n🎉 Embedding generation complete!")
    print(f"   Total movies embedded: {len(movies)}")
    print(f"   Collections created: movie_plot_embeddings")
    print("\n   Next step: Run 'make dev' to start the application")

if __name__ == "__main__":
    asyncio.run(main())
