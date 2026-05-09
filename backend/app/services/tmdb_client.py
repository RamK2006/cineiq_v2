import httpx
from typing import Dict, Any, List, Optional
import redis.asyncio as redis
import json
from ..core.config import settings

class TMDBClient:
    """Real TMDB API client with Redis caching"""
    
    BASE_URL = "https://api.themoviedb.org/3"
    IMAGE_BASE = "https://image.tmdb.org/t/p"
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.api_key = settings.TMDB_API_KEY
        self.cache_ttl = 21600  # 6 hours
    
    async def _make_request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """Make HTTP request to TMDB API with retry logic"""
        if params is None:
            params = {}
        params['api_key'] = self.api_key
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(f"{self.BASE_URL}{endpoint}", params=params)
                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPError as e:
                    if attempt == 2:
                        raise Exception(f"TMDB API error after 3 attempts: {str(e)}")
                    await asyncio.sleep(2 ** attempt)
    
    async def _get_cached(self, cache_key: str) -> Optional[Dict]:
        """Get data from Redis cache"""
        try:
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
        return None
    
    async def _set_cache(self, cache_key: str, data: Dict):
        """Set data in Redis cache"""
        try:
            await self.redis.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
        except Exception:
            pass
    
    async def get_movie(self, tmdb_id: int) -> Dict[str, Any]:
        """Get movie details by TMDB ID"""
        cache_key = f"tmdb:movie:{tmdb_id}"
        
        # Check cache
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        # Fetch from API
        movie = await self._make_request(f"/movie/{tmdb_id}")
        
        # Cache result
        await self._set_cache(cache_key, movie)
        
        return movie
    
    async def get_movie_credits(self, tmdb_id: int) -> Dict[str, Any]:
        """Get movie cast and crew"""
        cache_key = f"tmdb:credits:{tmdb_id}"
        
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        credits = await self._make_request(f"/movie/{tmdb_id}/credits")
        await self._set_cache(cache_key, credits)
        
        return credits
    
    async def get_movie_reviews(self, tmdb_id: int) -> List[Dict[str, Any]]:
        """Get movie reviews"""
        cache_key = f"tmdb:reviews:{tmdb_id}"
        
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        reviews = await self._make_request(f"/movie/{tmdb_id}/reviews")
        await self._set_cache(cache_key, reviews.get('results', []))
        
        return reviews.get('results', [])
    
    async def get_trending(self, time_window: str = "week") -> List[Dict[str, Any]]:
        """Get trending movies"""
        cache_key = f"tmdb:trending:{time_window}"
        
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        trending = await self._make_request(f"/trending/movie/{time_window}")
        results = trending.get('results', [])
        
        await self._set_cache(cache_key, results)
        return results
    
    async def get_popular(self, page: int = 1) -> List[Dict[str, Any]]:
        """Get popular movies"""
        cache_key = f"tmdb:popular:{page}"
        
        cached = await self._get_cached(cache_key)
        if cached:
            return cached
        
        popular = await self._make_request("/movie/popular", {"page": page})
        results = popular.get('results', [])
        
        await self._set_cache(cache_key, results)
        return results
    
    async def search_movie(self, query: str) -> List[Dict[str, Any]]:
        """Search movies by title"""
        search_results = await self._make_request("/search/movie", {"query": query})
        return search_results.get('results', [])
    
    def get_poster_url(self, poster_path: str, size: str = "w500") -> str:
        """Get full poster URL"""
        if not poster_path:
            return ""
        return f"{self.IMAGE_BASE}/{size}{poster_path}"
    
    def get_backdrop_url(self, backdrop_path: str, size: str = "w1280") -> str:
        """Get full backdrop URL"""
        if not backdrop_path:
            return ""
        return f"{self.IMAGE_BASE}/{size}{backdrop_path}"

import asyncio
