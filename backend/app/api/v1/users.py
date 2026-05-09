from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
from ...db.session import get_db
from ...db.models import User, Rating
from ...core.security import get_current_user
import uuid

router = APIRouter()

class RatingSubmission(BaseModel):
    tmdb_id: int
    rating: float  # 0.5 to 5.0
    watched_at: datetime = None

class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    display_name: str
    total_ratings: int
    average_rating: float
    taste_vector: List[float] = None
    top_genres: List[Dict[str, Any]]
    rating_distribution: Dict[str, int]

@router.post("/users/ratings")
async def submit_rating(
    submission: RatingSubmission,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Submit or update a movie rating"""
    
    # Validate rating
    if not (0.5 <= submission.rating <= 5.0):
        raise HTTPException(status_code=400, detail="Rating must be between 0.5 and 5.0")
    
    try:
        # Get or create user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Create new user
            user = User(
                id=uuid.uuid4(),
                clerk_id=user_id,
                email=f"{user_id}@temp.com",  # Will be updated by Clerk webhook
                display_name="User"
            )
            db.add(user)
            await db.flush()
        
        # Check if rating exists
        result = await db.execute(
            select(Rating).where(
                Rating.user_id == user.id,
                Rating.tmdb_id == submission.tmdb_id
            )
        )
        existing_rating = result.scalar_one_or_none()
        
        if existing_rating:
            # Update existing rating
            existing_rating.rating = submission.rating
            existing_rating.watched_at = submission.watched_at or datetime.utcnow()
            message = "Rating updated"
        else:
            # Create new rating
            new_rating = Rating(
                id=uuid.uuid4(),
                user_id=user.id,
                tmdb_id=submission.tmdb_id,
                rating=submission.rating,
                watched_at=submission.watched_at or datetime.utcnow(),
                source="manual"
            )
            db.add(new_rating)
            message = "Rating submitted"
        
        await db.commit()
        
        return {
            "success": True,
            "message": message,
            "tmdb_id": submission.tmdb_id,
            "rating": submission.rating
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit rating: {str(e)}")

@router.get("/users/ratings")
async def get_user_ratings(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get user's rating history"""
    
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"ratings": [], "total": 0}
        
        # Get ratings
        result = await db.execute(
            select(Rating)
            .where(Rating.user_id == user.id)
            .order_by(Rating.watched_at.desc())
            .limit(limit)
            .offset(offset)
        )
        ratings = result.scalars().all()
        
        # Get total count
        count_result = await db.execute(
            select(func.count(Rating.id)).where(Rating.user_id == user.id)
        )
        total = count_result.scalar()
        
        # Enrich with movie details
        from ...main import app_state
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        enriched_ratings = []
        for rating in ratings:
            try:
                movie = await tmdb.get_movie(rating.tmdb_id)
                enriched_ratings.append({
                    "tmdb_id": rating.tmdb_id,
                    "rating": rating.rating,
                    "watched_at": rating.watched_at.isoformat(),
                    "title": movie.get("title", ""),
                    "poster_url": tmdb.get_poster_url(movie.get("poster_path", "")),
                    "release_date": movie.get("release_date", ""),
                    "genres": [g["name"] for g in movie.get("genres", [])]
                })
            except:
                enriched_ratings.append({
                    "tmdb_id": rating.tmdb_id,
                    "rating": rating.rating,
                    "watched_at": rating.watched_at.isoformat(),
                    "title": "Unknown",
                    "poster_url": "",
                    "release_date": "",
                    "genres": []
                })
        
        return {
            "ratings": enriched_ratings,
            "total": total,
            "page": offset // limit + 1,
            "pages": (total + limit - 1) // limit
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ratings: {str(e)}")

@router.get("/users/profile")
async def get_user_profile(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user taste profile with genre affinities and statistics"""
    
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all ratings
        result = await db.execute(
            select(Rating).where(Rating.user_id == user.id)
        )
        ratings = result.scalars().all()
        
        if not ratings:
            return {
                "user_id": user_id,
                "email": user.email,
                "display_name": user.display_name,
                "total_ratings": 0,
                "average_rating": 0.0,
                "top_genres": [],
                "rating_distribution": {},
                "taste_evolution": []
            }
        
        # Calculate statistics
        total_ratings = len(ratings)
        average_rating = sum(r.rating for r in ratings) / total_ratings
        
        # Rating distribution
        rating_distribution = {
            "5.0": 0, "4.5": 0, "4.0": 0, "3.5": 0, "3.0": 0,
            "2.5": 0, "2.0": 0, "1.5": 0, "1.0": 0, "0.5": 0
        }
        for rating in ratings:
            key = f"{rating.rating:.1f}"
            if key in rating_distribution:
                rating_distribution[key] += 1
        
        # Fetch genre data
        from ...main import app_state
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        genre_ratings = {}
        for rating in ratings[:50]:  # Limit to recent 50 for performance
            try:
                movie = await tmdb.get_movie(rating.tmdb_id)
                for genre in movie.get("genres", []):
                    genre_name = genre["name"]
                    if genre_name not in genre_ratings:
                        genre_ratings[genre_name] = []
                    genre_ratings[genre_name].append(rating.rating)
            except:
                continue
        
        # Calculate genre affinities
        top_genres = []
        for genre, ratings_list in genre_ratings.items():
            avg_rating = sum(ratings_list) / len(ratings_list)
            top_genres.append({
                "genre": genre,
                "average_rating": round(avg_rating, 2),
                "count": len(ratings_list),
                "affinity": round(avg_rating / 5.0, 2)  # Normalized 0-1
            })
        
        top_genres.sort(key=lambda x: x["average_rating"], reverse=True)
        
        return {
            "user_id": user_id,
            "email": user.email,
            "display_name": user.display_name,
            "total_ratings": total_ratings,
            "average_rating": round(average_rating, 2),
            "top_genres": top_genres[:10],
            "rating_distribution": rating_distribution,
            "taste_vector": user.taste_vector or []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile: {str(e)}")

@router.delete("/users/ratings/{tmdb_id}")
async def delete_rating(
    tmdb_id: int,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a rating"""
    
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Find and delete rating
        result = await db.execute(
            select(Rating).where(
                Rating.user_id == user.id,
                Rating.tmdb_id == tmdb_id
            )
        )
        rating = result.scalar_one_or_none()
        
        if not rating:
            raise HTTPException(status_code=404, detail="Rating not found")
        
        await db.delete(rating)
        await db.commit()
        
        return {
            "success": True,
            "message": "Rating deleted",
            "tmdb_id": tmdb_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete rating: {str(e)}")
