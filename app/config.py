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

    # VTON
    VTON_METHOD: str = "vertex_ai" # run_vton or vertex_ai

    # Admin credentials
    ADMIN_USERNAME: str = "cookie8744@hanyang.ac.kr"
    ADMIN_PASSWORD: str = "admin"

    # Shop User ID - clothes from this user will be visible to all
    SHOP_USER_ID: int = 1 # Default shop user ID, can be overridden by environment variable

    # Supabase(DB)
    SUPABASE_URL:str
    SUPABASE_KEY:str
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None

    GOOGLE_CLOUD_PROJECT: str
    GOOGLE_APPLICATION_CREDENTIALS: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()

# Ensure resource directories exist
os.makedirs(settings.PERSON_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.CLOTH_RESOURCE_DIR, exist_ok=True)
os.makedirs(settings.RESULT_RESOURCE_DIR, exist_ok=True)
