from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Vibe-Checker Backend"
    APP_ENV: str = Field(default="local", env="APP_ENV")
    PORT: int = 8000
    FRONTEND_URL: str = Field(default="http://localhost:3000", env="FRONTEND_URL")

    # API Keys / External Services
    GROQ_API_KEY: str = Field(..., env="GROQ_API_KEY")
    
    QDRANT_URL: str = Field(..., env="QDRANT_URL")
    QDRANT_API_KEY: str = Field(..., env="QDRANT_API_KEY")
    
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_ANON_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_KEY")
    
    REDIS_URL: str = Field(..., env="REDIS_URL")
    
    # Dataset & Embeddings
    HF_DATASET_PATH: str = "maharshipandya/spotify-tracks-dataset"
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    class Config:
        env_file = (".env", "../.env")
        env_file_encoding = "utf-8"

settings = Settings()
