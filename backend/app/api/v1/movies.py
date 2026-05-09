from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from ...db.session import get_db
from ...db.models import Movie
from ...core.security import get_current_user
from ...services.tmdb_client import TMDBClient
import redis.asyncio as redis

router = APIRouter()

@router.get("/movies/trending")
async def get_trending_movies(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get trending movies from TMDB"""
    # Get Redis client from app state
    from ...main import app_state
    redis_client = app_state.get("redis")
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis not available")
    
    tmdb = TMDBClient(redis_client)
    
    try:
        trending = await tmdb.get_trending("week")
        
        # Enrich with poster URLs
        for movie in trending:
            movie['poster_url'] = tmdb.get_poster_url(movie.get('poster_path', ''))
            movie['backdrop_url'] = tmdb.get_backdrop_url(movie.get('backdrop_path', ''))
        
        return {
            "movies": trending[:20],
            "total": len(trending)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending movies: {str(e)}")

@router.get("/movies/{tmdb_id}")
async def get_movie_detail(
    tmdb_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed movie information"""
    from ...main import app_state
    redis_client = app_state.get("redis")
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis not available")
    
    tmdb = TMDBClient(redis_client)
    
    try:
        # Fetch movie details
        movie = await tmdb.get_movie(tmdb_id)
        credits = await tmdb.get_movie_credits(tmdb_id)
        reviews = await tmdb.get_movie_reviews(tmdb_id)
        
        # Extract director
        director = None
        for crew in credits.get('crew', []):
            if crew.get('job') == 'Director':
                director = crew.get('name')
                break
        
        # Extract top cast
        cast = [
            {
                'name': actor['name'],
                'character': actor.get('character', ''),
                'profile_path': actor.get('profile_path', '')
            }
            for actor in credits.get('cast', [])[:10]
        ]
        
        # Build response
        response = {
            'tmdb_id': movie['id'],
            'title': movie.get('title', ''),
            'overview': movie.get('overview', ''),
            'release_date': movie.get('release_date', ''),
            'runtime': movie.get('runtime'),
            'genres': [g['name'] for g in movie.get('genres', [])],
            'director': director,
            'cast': cast,
            'vote_average': movie.get('vote_average', 0.0),
            'vote_count': movie.get('vote_count', 0),
            'popularity': movie.get('popularity', 0.0),
            'poster_url': tmdb.get_poster_url(movie.get('poster_path', '')),
            'backdrop_url': tmdb.get_backdrop_url(movie.get('backdrop_path', '')),
            'tagline': movie.get('tagline', ''),
            'budget': movie.get('budget', 0),
            'revenue': movie.get('revenue', 0),
            'reviews_count': len(reviews)
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch movie: {str(e)}")

@router.get("/movies/search")
async def search_movies(
    query: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Search movies by title"""
    from ...main import app_state
    redis_client = app_state.get("redis")
    
    if not redis_client:
        raise HTTPException(status_code=500, detail="Redis not available")
    
    tmdb = TMDBClient(redis_client)
    
    try:
        results = await tmdb.search_movie(query)
        
        # Enrich with URLs
        for movie in results:
            movie['poster_url'] = tmdb.get_poster_url(movie.get('poster_path', ''))
        
        return {
            "query": query,
            "results": results[:20],
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
