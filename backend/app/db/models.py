from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
import enum

Base = declarative_base()


class RatingSource(str, enum.Enum):
    MANUAL = "manual"
    IMPORT = "import"
    IMPLICIT = "implicit"


class ImportSource(str, enum.Enum):
    LETTERBOXD = "letterboxd"
    TRAKT = "trakt"


class ImportStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    display_name = Column(String)
    taste_vector = Column(ARRAY(Float))  # Genre affinity vector
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    tmdb_id = Column(Integer, nullable=False, index=True)
    rating = Column(Float, nullable=False)  # 0.5 to 5.0
    watched_at = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(Enum(RatingSource), default=RatingSource.MANUAL)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WatchSession(Base):
    __tablename__ = "watch_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    room_id = Column(UUID(as_uuid=True), unique=True, nullable=False, index=True)
    host_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tmdb_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True))
    max_participants = Column(Integer, default=10)


class WatchParticipant(Base):
    __tablename__ = "watch_participants"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("watch_sessions.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    left_at = Column(DateTime(timezone=True))


class ImportJob(Base):
    __tablename__ = "import_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    source = Column(Enum(ImportSource), nullable=False)
    status = Column(Enum(ImportStatus), default=ImportStatus.PENDING)
    total_items = Column(Integer, default=0)
    processed_items = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class Movie(Base):
    """Cache table for TMDB movie metadata"""
    __tablename__ = "movies"
    
    tmdb_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    overview = Column(Text)
    release_date = Column(String)
    genres = Column(JSON)  # List of genre names
    director = Column(String)
    cast = Column(JSON)  # List of actor names
    poster_path = Column(String)
    backdrop_path = Column(String)
    runtime = Column(Integer)
    vote_average = Column(Float)
    vote_count = Column(Integer)
    popularity = Column(Float)
    keywords = Column(JSON)  # List of keywords
    cached_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
