from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./resources/app.db"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Resource Directories
    PERSON_RESOURCE_DIR: str = "resources/persons"
    CLOTH_RESOURCE_DIR: str = "resources/cloths"
    RESULT_RESOURCE_DIR: str = "resources/results"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()

# Ensure resource directories exist
os.makedirs(settings.PERSON_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.CLOTH_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.RESULT_RESOURCE_DIR, exist_ok=True)
