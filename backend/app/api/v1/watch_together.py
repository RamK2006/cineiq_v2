from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime
from ...db.session import get_db
from ...db.models import WatchSession, WatchParticipant, User
from ...core.security import get_current_user
from ...websocket.manager import manager
from sqlalchemy import select

router = APIRouter()

class CreateRoomRequest(BaseModel):
    tmdb_id: int
    max_participants: int = 10

@router.post("/rooms/create")
async def create_watch_room(
    request: CreateRoomRequest,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new watch-together room"""
    
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
        
        # Create watch session
        room_id = uuid.uuid4()
        session = WatchSession(
            id=uuid.uuid4(),
            room_id=room_id,
            host_user_id=user.id,
            tmdb_id=request.tmdb_id,
            max_participants=request.max_participants
        )
        db.add(session)
        
        # Add host as participant
        participant = WatchParticipant(
            id=uuid.uuid4(),
            session_id=session.id,
            user_id=user.id
        )
        db.add(participant)
        
        await db.commit()
        
        # Get movie details
        from ...main import app_state
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        movie = await tmdb.get_movie(request.tmdb_id)
        
        return {
            "room_id": str(room_id),
            "join_url": f"/watch/{room_id}",
            "ws_url": f"ws://localhost:8000/api/v1/ws/room/{room_id}",
            "movie": {
                "tmdb_id": request.tmdb_id,
                "title": movie.get("title", ""),
                "poster_url": tmdb.get_poster_url(movie.get("poster_path", ""))
            },
            "created_at": session.created_at.isoformat()
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")

@router.get("/rooms/{room_id}")
async def get_room_info(
    room_id: str,
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get room information and participants"""
    
    try:
        # Get session
        result = await db.execute(
            select(WatchSession).where(WatchSession.room_id == uuid.UUID(room_id))
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Room not found")
        
        # Get participants
        result = await db.execute(
            select(WatchParticipant, User)
            .join(User, WatchParticipant.user_id == User.id)
            .where(WatchParticipant.session_id == session.id)
            .where(WatchParticipant.left_at.is_(None))
        )
        participants_data = result.all()
        
        participants = [
            {
                "user_id": str(user.id),
                "display_name": user.display_name,
                "joined_at": participant.joined_at.isoformat()
            }
            for participant, user in participants_data
        ]
        
        # Get movie details
        from ...main import app_state
        from ...services.tmdb_client import TMDBClient
        redis_client = app_state.get("redis")
        tmdb = TMDBClient(redis_client)
        
        movie = await tmdb.get_movie(session.tmdb_id)
        
        # Get live participants from WebSocket manager
        live_participants = manager.get_room_participants(room_id)
        
        return {
            "room_id": room_id,
            "movie": {
                "tmdb_id": session.tmdb_id,
                "title": movie.get("title", ""),
                "poster_url": tmdb.get_poster_url(movie.get("poster_path", "")),
                "backdrop_url": tmdb.get_backdrop_url(movie.get("backdrop_path", ""))
            },
            "host_user_id": str(session.host_user_id),
            "participants": participants,
            "live_participants": live_participants,
            "max_participants": session.max_participants,
            "created_at": session.created_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch room: {str(e)}")

@router.websocket("/ws/room/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str):
    """WebSocket endpoint for watch-together room"""
    
    # Get user info from query params
    user_id = websocket.query_params.get("user_id", "anonymous")
    display_name = websocket.query_params.get("display_name", "Guest")
    
    await manager.connect(websocket, room_id, user_id, display_name)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_json()
            message_type = data.get("type")
            
            if message_type == "playback":
                # Handle playback events (play, pause, seek)
                await manager.handle_playback_event(websocket, data)
            
            elif message_type == "chat":
                # Handle chat messages
                await manager.handle_chat_message(websocket, data)
            
            elif message_type == "reaction":
                # Handle emoji reactions
                await manager.handle_reaction(websocket, data)
            
            elif message_type == "ping":
                # Heartbeat
                await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)
