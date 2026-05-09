from fastapi import WebSocket
from typing import Dict, Set, List
import json
from datetime import datetime
import uuid

class ConnectionManager:
    """Manages WebSocket connections for watch-together rooms"""
    
    def __init__(self):
        # room_id -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        
        # room_id -> room state
        self.room_states: Dict[str, dict] = {}
        
        # websocket -> user info
        self.connection_users: Dict[WebSocket, dict] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str, display_name: str):
        """Connect a user to a room"""
        await websocket.accept()
        
        # Add to room
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
            self.room_states[room_id] = {
                "playback_state": "paused",
                "current_time": 0,
                "host_user_id": user_id,
                "created_at": datetime.utcnow().isoformat()
            }
        
        self.active_connections[room_id].add(websocket)
        self.connection_users[websocket] = {
            "user_id": user_id,
            "display_name": display_name,
            "room_id": room_id
        }
        
        # Notify others
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "user_id": user_id,
            "display_name": display_name,
            "timestamp": datetime.utcnow().isoformat(),
            "participants_count": len(self.active_connections[room_id])
        }, exclude=websocket)
        
        # Send current state to new user
        await websocket.send_json({
            "type": "room_state",
            "state": self.room_states[room_id],
            "participants_count": len(self.active_connections[room_id])
        })
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a user from their room"""
        if websocket not in self.connection_users:
            return
        
        user_info = self.connection_users[websocket]
        room_id = user_info["room_id"]
        
        # Remove from room
        if room_id in self.active_connections:
            self.active_connections[room_id].discard(websocket)
            
            # Notify others
            import asyncio
            asyncio.create_task(
                self.broadcast_to_room(room_id, {
                    "type": "user_left",
                    "user_id": user_info["user_id"],
                    "display_name": user_info["display_name"],
                    "timestamp": datetime.utcnow().isoformat(),
                    "participants_count": len(self.active_connections[room_id])
                })
            )
            
            # Clean up empty rooms
            if len(self.active_connections[room_id]) == 0:
                del self.active_connections[room_id]
                del self.room_states[room_id]
        
        del self.connection_users[websocket]
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude: WebSocket = None):
        """Broadcast message to all users in a room"""
        if room_id not in self.active_connections:
            return
        
        disconnected = []
        for connection in self.active_connections[room_id]:
            if connection == exclude:
                continue
            
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Clean up disconnected
        for connection in disconnected:
            self.disconnect(connection)
    
    async def handle_playback_event(self, websocket: WebSocket, event: dict):
        """Handle playback control events (play, pause, seek)"""
        if websocket not in self.connection_users:
            return
        
        user_info = self.connection_users[websocket]
        room_id = user_info["room_id"]
        
        # Update room state
        if room_id in self.room_states:
            state = self.room_states[room_id]
            
            if event["action"] == "play":
                state["playback_state"] = "playing"
                state["current_time"] = event.get("time", state["current_time"])
            elif event["action"] == "pause":
                state["playback_state"] = "paused"
                state["current_time"] = event.get("time", state["current_time"])
            elif event["action"] == "seek":
                state["current_time"] = event.get("time", 0)
            
            # Broadcast to room
            await self.broadcast_to_room(room_id, {
                "type": "playback_sync",
                "action": event["action"],
                "time": state["current_time"],
                "state": state["playback_state"],
                "user_id": user_info["user_id"],
                "display_name": user_info["display_name"],
                "timestamp": datetime.utcnow().isoformat()
            }, exclude=websocket)
    
    async def handle_chat_message(self, websocket: WebSocket, message: dict):
        """Handle chat messages"""
        if websocket not in self.connection_users:
            return
        
        user_info = self.connection_users[websocket]
        room_id = user_info["room_id"]
        
        # Broadcast chat message
        await self.broadcast_to_room(room_id, {
            "type": "chat_message",
            "message": message.get("text", ""),
            "user_id": user_info["user_id"],
            "display_name": user_info["display_name"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    async def handle_reaction(self, websocket: WebSocket, reaction: dict):
        """Handle emoji reactions"""
        if websocket not in self.connection_users:
            return
        
        user_info = self.connection_users[websocket]
        room_id = user_info["room_id"]
        
        # Broadcast reaction
        await self.broadcast_to_room(room_id, {
            "type": "reaction",
            "emoji": reaction.get("emoji", "❤️"),
            "user_id": user_info["user_id"],
            "display_name": user_info["display_name"],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    def get_room_participants(self, room_id: str) -> List[dict]:
        """Get list of participants in a room"""
        if room_id not in self.active_connections:
            return []
        
        participants = []
        for connection in self.active_connections[room_id]:
            if connection in self.connection_users:
                user_info = self.connection_users[connection]
                participants.append({
                    "user_id": user_info["user_id"],
                    "display_name": user_info["display_name"]
                })
        
        return participants

# Global connection manager instance
manager = ConnectionManager()
