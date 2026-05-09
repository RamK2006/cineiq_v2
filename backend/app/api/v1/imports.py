from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import csv
import io
import uuid
from datetime import datetime
from ...db.session import get_db
from ...db.models import User, Rating, ImportJob, ImportSource, ImportStatus
from ...core.security import get_current_user

router = APIRouter()

@router.post("/import/letterboxd")
async def import_letterboxd(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Import ratings from Letterboxd CSV export
    Expected columns: Date, Name, Year, Letterboxd URI, Rating
    """
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Get or create user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            user = User(
                id=uuid.uuid4(),
                clerk_id=user_id,
                email=f"{user_id}@temp.com",
                display_name="User"
            )
            db.add(user)
            await db.flush()
        
        # Create import job
        job = ImportJob(
            id=uuid.uuid4(),
            user_id=user.id,
            source=ImportSource.LETTERBOXD,
            status=ImportStatus.PROCESSING
        )
        db.add(job)
        await db.flush()
        
        # Read CSV
        contents = await file.read()
        csv_data = io.StringIO(contents.decode('utf-8'))
        reader = csv.DictReader(csv_data)
        
        # Get TMDB client
        from ...main import app_state
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        imported_count = 0
        failed_count = 0
        total_count = 0
        
        for row in reader:
            total_count += 1
            
            try:
                # Extract data
                title = row.get('Name', '')
                year = row.get('Year', '')
                rating_str = row.get('Rating', '')
                date_str = row.get('Date', '')
                
                if not title or not rating_str:
                    failed_count += 1
                    continue
                
                # Convert Letterboxd rating (0.5-5.0 stars) to our format
                rating = float(rating_str)
                
                # Search for movie on TMDB
                search_query = f"{title} {year}" if year else title
                search_results = await tmdb.search_movie(search_query)
                
                if not search_results:
                    failed_count += 1
                    continue
                
                # Use first result
                tmdb_id = search_results[0]['id']
                
                # Parse date
                watched_at = None
                if date_str:
                    try:
                        watched_at = datetime.strptime(date_str, '%Y-%m-%d')
                    except:
                        watched_at = datetime.utcnow()
                else:
                    watched_at = datetime.utcnow()
                
                # Check if rating already exists
                result = await db.execute(
                    select(Rating).where(
                        Rating.user_id == user.id,
                        Rating.tmdb_id == tmdb_id
                    )
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    # Update
                    existing.rating = rating
                    existing.watched_at = watched_at
                    existing.source = "import"
                else:
                    # Create new
                    new_rating = Rating(
                        id=uuid.uuid4(),
                        user_id=user.id,
                        tmdb_id=tmdb_id,
                        rating=rating,
                        watched_at=watched_at,
                        source="import"
                    )
                    db.add(new_rating)
                
                imported_count += 1
                
                # Commit in batches
                if imported_count % 10 == 0:
                    job.processed_items = imported_count
                    await db.commit()
                
            except Exception as e:
                print(f"Failed to import row: {str(e)}")
                failed_count += 1
                continue
        
        # Update job status
        job.status = ImportStatus.COMPLETED
        job.total_items = total_count
        job.processed_items = imported_count
        job.completed_at = datetime.utcnow()
        
        await db.commit()
        
        return {
            "success": True,
            "job_id": str(job.id),
            "total_items": total_count,
            "imported": imported_count,
            "failed": failed_count,
            "message": f"Successfully imported {imported_count} out of {total_count} ratings"
        }
        
    except Exception as e:
        await db.rollback()
        
        # Update job status to failed
        if 'job' in locals():
            job.status = ImportStatus.FAILED
            job.error_message = str(e)
            await db.commit()
        
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@router.get("/import/jobs")
async def get_import_jobs(
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's import job history"""
    
    try:
        # Get user
        result = await db.execute(
            select(User).where(User.clerk_id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return {"jobs": []}
        
        # Get jobs
        result = await db.execute(
            select(ImportJob)
            .where(ImportJob.user_id == user.id)
            .order_by(ImportJob.created_at.desc())
        )
        jobs = result.scalars().all()
        
        return {
            "jobs": [
                {
                    "job_id": str(job.id),
                    "source": job.source.value,
                    "status": job.status.value,
                    "total_items": job.total_items,
                    "processed_items": job.processed_items,
                    "error_message": job.error_message,
                    "created_at": job.created_at.isoformat(),
                    "completed_at": job.completed_at.isoformat() if job.completed_at else None
                }
                for job in jobs
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch jobs: {str(e)}")
