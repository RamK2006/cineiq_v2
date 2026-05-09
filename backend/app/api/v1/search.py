from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ...core.security import get_current_user
from ...services.embedding import EmbeddingService
from qdrant_client.models import Filter, FieldCondition, MatchValue

router = APIRouter()

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 20
    genres: Optional[List[str]] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None

@router.post("/search/semantic")
async def semantic_search(
    request: SemanticSearchRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Semantic search using natural language queries
    Example: "dark psychological thriller with twist ending"
    """
    from ...main import app_state
    
    # Get services
    qdrant = app_state.get("qdrant")
    embedding_service = app_state.get("embedding_service")
    
    if not qdrant or not embedding_service:
        raise HTTPException(status_code=500, detail="Search services not available")
    
    try:
        # Generate query embedding
        query_vector = embedding_service.encode_single(request.query)
        
        # Build filter
        filter_conditions = []
        
        if request.genres:
            for genre in request.genres:
                filter_conditions.append(
                    FieldCondition(
                        key="genres",
                        match=MatchValue(value=genre)
                    )
                )
        
        search_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        # Search in Qdrant
        search_results = qdrant.search(
            collection_name="movie_plot_embeddings",
            query_vector=query_vector.tolist(),
            limit=request.limit,
            query_filter=search_filter
        )
        
        # Format results
        results = []
        for hit in search_results:
            results.append({
                "tmdb_id": hit.payload.get("tmdb_id"),
                "title": hit.payload.get("title"),
                "overview": hit.payload.get("overview"),
                "genres": hit.payload.get("genres", []),
                "year": hit.payload.get("year"),
                "rating": hit.payload.get("rating"),
                "similarity_score": hit.score,
                "match_reason": f"Semantic similarity: {hit.score:.2%}"
            })
        
        return {
            "query": request.query,
            "results": results,
            "total": len(results)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Semantic search failed: {str(e)}")

@router.get("/search/vibe")
async def vibe_search(
    vibe: str,
    limit: int = 20,
    user_id: str = Depends(get_current_user)
):
    """
    Quick vibe-based search
    Examples: "mind-bending", "feel-good", "dark and atmospheric"
    """
    # Map common vibes to search queries
    vibe_queries = {
        "mind-bending": "complex psychological thriller with plot twists and non-linear narrative",
        "feel-good": "uplifting heartwarming comedy with happy ending",
        "dark-atmospheric": "dark moody atmospheric thriller with suspense",
        "action-packed": "intense action adventure with explosions and fights",
        "romantic": "romantic love story with emotional depth",
        "scary": "horror thriller with suspense and jump scares",
        "funny": "comedy with humor and laughs",
        "epic": "epic adventure with grand scale and heroic journey"
    }
    
    # Get query or use vibe directly
    query = vibe_queries.get(vibe.lower().replace(" ", "-"), vibe)
    
    # Use semantic search
    request = SemanticSearchRequest(query=query, limit=limit)
    return await semantic_search(request, user_id)
