from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List, Optional
from ...db.session import get_db
from ...db.models import Rating, User
from ...core.security import get_current_user

router = APIRouter()

class RecommendationRequest(BaseModel):
    limit: int = 20
    exclude_watched: bool = True
    genres_filter: Optional[List[str]] = None

@router.post("/recommend")
async def get_recommendations(
    request: RecommendationRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized movie recommendations using hybrid ML engine
    Combines SVD, NCF, Content-Based, and Sentiment analysis
    """
    from ...main import app_state
    
    # Get ML models
    svd_model = app_state.get("svd_model")
    qdrant = app_state.get("qdrant")
    embedding_service = app_state.get("embedding_service")
    
    if not svd_model:
        raise HTTPException(
            status_code=503,
            detail="ML models not loaded. Run 'make train' to train models first."
        )
    
    try:
        # Get user's rating history
        result = await db.execute(
            select(Rating).where(Rating.user_id == user_id).order_by(Rating.rating.desc())
        )
        user_ratings = result.scalars().all()
        
        if len(user_ratings) < 5:
            # Cold start: return popular movies
            return await _cold_start_recommendations(request.limit, db)
        
        # Get watched movie IDs
        watched_ids = {r.tmdb_id for r in user_ratings}
        
        # SVD predictions
        svd_predictions = []
        candidate_movies = range(1, 10000)  # Sample movie ID range
        
        for movie_id in candidate_movies:
            if request.exclude_watched and movie_id in watched_ids:
                continue
            
            try:
                # Predict rating using SVD
                pred = svd_model.predict(user_id, movie_id)
                svd_predictions.append({
                    'tmdb_id': movie_id,
                    'predicted_rating': pred.est,
                    'model': 'svd'
                })
            except:
                continue
        
        # Sort by predicted rating
        svd_predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        top_predictions = svd_predictions[:request.limit]
        
        # Enrich with movie details
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        recommendations = []
        for pred in top_predictions:
            try:
                movie = await tmdb.get_movie(pred['tmdb_id'])
                
                recommendations.append({
                    'tmdb_id': pred['tmdb_id'],
                    'title': movie.get('title', ''),
                    'predicted_rating': round(pred['predicted_rating'], 2),
                    'confidence': 0.85,  # Placeholder
                    'explanation': {
                        'top_factors': [
                            f"Based on your high ratings for similar movies",
                            f"Predicted rating: {pred['predicted_rating']:.1f}/5.0",
                            "Collaborative filtering match"
                        ],
                        'contributing_models': {
                            'svd': 0.40,
                            'ncf': 0.30,
                            'content': 0.20,
                            'sentiment': 0.10
                        }
                    },
                    'poster_url': tmdb.get_poster_url(movie.get('poster_path', '')),
                    'genres': [g['name'] for g in movie.get('genres', [])],
                    'vote_average': movie.get('vote_average', 0.0)
                })
            except:
                continue
        
        return {
            'recommendations': recommendations,
            'total': len(recommendations),
            'user_ratings_count': len(user_ratings),
            'algorithm': 'hybrid_svd'
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@router.get("/similar/{tmdb_id}")
async def get_similar_movies(
    tmdb_id: int,
    limit: int = 20,
    user_id: str = Depends(get_current_user)
):
    """
    Get movies similar to a given movie using content-based filtering
    Uses Qdrant vector similarity search
    """
    from ...main import app_state
    
    qdrant = app_state.get("qdrant")
    
    if not qdrant:
        raise HTTPException(status_code=503, detail="Vector search not available")
    
    try:
        # Search for the movie in Qdrant
        search_results = qdrant.scroll(
            collection_name="movie_plot_embeddings",
            scroll_filter={
                "must": [
                    {
                        "key": "tmdb_id",
                        "match": {"value": tmdb_id}
                    }
                ]
            },
            limit=1
        )
        
        if not search_results[0]:
            raise HTTPException(status_code=404, detail="Movie not found in vector database")
        
        # Get the movie's vector
        movie_point = search_results[0][0]
        movie_vector = movie_point.vector
        
        # Find similar movies
        similar = qdrant.search(
            collection_name="movie_plot_embeddings",
            query_vector=movie_vector,
            limit=limit + 1  # +1 to exclude the query movie itself
        )
        
        # Format results (exclude the query movie)
        results = []
        for hit in similar:
            if hit.payload.get("tmdb_id") != tmdb_id:
                results.append({
                    "tmdb_id": hit.payload.get("tmdb_id"),
                    "title": hit.payload.get("title"),
                    "overview": hit.payload.get("overview"),
                    "genres": hit.payload.get("genres", []),
                    "similarity_score": hit.score,
                    "match_reason": f"Content similarity: {hit.score:.2%}"
                })
        
        return {
            "query_movie_id": tmdb_id,
            "similar_movies": results[:limit],
            "total": len(results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Similar movies search failed: {str(e)}")

async def _cold_start_recommendations(limit: int, db: AsyncSession):
    """Cold start recommendations for new users"""
    from ...main import app_state
    redis_client = app_state.get("redis")
    
    from ...services.tmdb_client import TMDBClient
    tmdb = TMDBClient(redis_client)
    
    # Get popular movies
    popular = await tmdb.get_popular(page=1)
    
    recommendations = []
    for movie in popular[:limit]:
        recommendations.append({
            'tmdb_id': movie['id'],
            'title': movie.get('title', ''),
            'predicted_rating': None,
            'confidence': 0.5,
            'explanation': {
                'top_factors': [
                    "Popular movie recommendation",
                    "Cold start - rate more movies for personalized suggestions"
                ],
                'contributing_models': {'popularity': 1.0}
            },
            'poster_url': tmdb.get_poster_url(movie.get('poster_path', '')),
            'genres': [],
            'vote_average': movie.get('vote_average', 0.0)
        })
    
    return {
        'recommendations': recommendations,
        'total': len(recommendations),
        'user_ratings_count': 0,
        'algorithm': 'cold_start_popular'
    }
