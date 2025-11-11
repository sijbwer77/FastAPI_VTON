from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # CORS
    ALLOWED_ORIGINS: List[str]

    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    # Google OAuth
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    # Resource Directories
    PERSON_RESOURCE_DIR: str = "resources/persons"
    CLOTH_RESOURCE_DIR: str = "resources/cloths"
    RESULT_RESOURCE_DIR: str = "resources/results"

    # VTON (original, vertex_ai)
    VTON_METHOD: str = "original"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Ensure resource directories exist
os.makedirs(settings.PERSON_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.CLOTH_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.RESULT_RESOURCE_DIR, exist_ok=True)
