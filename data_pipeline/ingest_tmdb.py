"""
Ingest TMDB movie data into PostgreSQL
"""
import os
import asyncio
import httpx
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.core.config import settings
from backend.app.db.models import Movie, Base

async def fetch_tmdb_movies(api_key: str, pages: int = 10):
    """Fetch popular movies from TMDB"""
    base_url = "https://api.themoviedb.org/3"
    movies = []
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Fetch popular movies
        for page in range(1, pages + 1):
            print(f"📥 Fetching page {page}/{pages}...")
            
            try:
                response = await client.get(
                    f"{base_url}/movie/popular",
                    params={"api_key": api_key, "page": page}
                )
                response.raise_for_status()
                data = response.json()
                
                for movie in data.get('results', []):
                    # Fetch detailed info
                    detail_response = await client.get(
                        f"{base_url}/movie/{movie['id']}",
                        params={"api_key": api_key}
                    )
                    detail = detail_response.json()
                    
                    # Fetch credits
                    credits_response = await client.get(
                        f"{base_url}/movie/{movie['id']}/credits",
                        params={"api_key": api_key}
                    )
                    credits = credits_response.json()
                    
                    # Extract director
                    director = None
                    for crew in credits.get('crew', []):
                        if crew.get('job') == 'Director':
                            director = crew.get('name')
                            break
                    
                    # Extract top cast
                    cast = [actor['name'] for actor in credits.get('cast', [])[:5]]
                    
                    # Extract genres
                    genres = [g['name'] for g in detail.get('genres', [])]
                    
                    movies.append({
                        'tmdb_id': movie['id'],
                        'title': movie.get('title', ''),
                        'overview': movie.get('overview', ''),
                        'release_date': movie.get('release_date', ''),
                        'genres': genres,
                        'director': director,
                        'cast': cast,
                        'poster_path': movie.get('poster_path', ''),
                        'backdrop_path': movie.get('backdrop_path', ''),
                        'runtime': detail.get('runtime'),
                        'vote_average': movie.get('vote_average', 0.0),
                        'vote_count': movie.get('vote_count', 0),
                        'popularity': movie.get('popularity', 0.0),
                        'keywords': []
                    })
                    
                    print(f"   ✓ {movie.get('title', 'Unknown')}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"   ✗ Error on page {page}: {str(e)}")
                continue
    
    return movies

async def store_movies(movies: list):
    """Store movies in PostgreSQL"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    
    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        for movie_data in movies:
            # Check if exists
            result = await session.execute(
                select(Movie).where(Movie.tmdb_id == movie_data['tmdb_id'])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update
                for key, value in movie_data.items():
                    setattr(existing, key, value)
            else:
                # Insert
                movie = Movie(**movie_data)
                session.add(movie)
        
        await session.commit()
    
    await engine.dispose()

async def main():
    """Main ingestion function"""
    print("🎬 TMDB Movie Data Ingestion")
    print("=" * 50)
    
    api_key = settings.TMDB_API_KEY
    if not api_key or api_key == "REPLACE_WITH_YOUR_KEY":
        print("❌ Error: TMDB_API_KEY not set in .env file")
        print("   Get your API key from: https://www.themoviedb.org/settings/api")
        return
    
    print(f"🔑 Using TMDB API key: {api_key[:10]}...")
    
    # Fetch movies
    print("\n📥 Fetching movies from TMDB...")
    movies = await fetch_tmdb_movies(api_key, pages=5)  # Fetch 5 pages = ~100 movies
    
    print(f"\n✅ Fetched {len(movies)} movies")
    
    # Store in database
    print("\n💾 Storing in PostgreSQL...")
    await store_movies(movies)
    
    print(f"\n🎉 Successfully ingested {len(movies)} movies!")
    print("   Next step: Run 'make build-embeddings' to generate vector embeddings")

if __name__ == "__main__":
    asyncio.run(main())
