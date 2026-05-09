from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://cineiq:cineiq_password@localhost:5432/cineiq"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Qdrant
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    
    # Clerk Authentication
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    
    # TMDB API
    TMDB_API_KEY: str
    
    # Groq API
    GROQ_API_KEY: str
    
    # ML Model Paths
    SVD_MODEL_PATH: str = "./backend/app/ml/models/svd_v1.pkl"
    NCF_MODEL_PATH: str = "./backend/app/ml/models/ncf_v1.pt"
    
    # S3/MinIO
    S3_BUCKET: Optional[str] = "cineiq-posters"
    S3_ENDPOINT_URL: Optional[str] = "http://localhost:9000"
    AWS_ACCESS_KEY_ID: Optional[str] = "minioadmin"
    AWS_SECRET_ACCESS_KEY: Optional[str] = "minioadmin"
    
    # Ensemble Weights
    ENSEMBLE_WEIGHT_SVD: float = 0.40
    ENSEMBLE_WEIGHT_NCF: float = 0.30
    ENSEMBLE_WEIGHT_CONTENT: float = 0.20
    ENSEMBLE_WEIGHT_SENTIMENT: float = 0.10
    
    # Application
    APP_NAME: str = "CINEIQ"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
