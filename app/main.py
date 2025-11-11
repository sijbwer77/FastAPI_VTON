# app/main.py
import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware # Import SessionMiddleware
from fastapi.staticfiles import StaticFiles

from app import models
from app.database import engine
from app.config import settings

# Add project path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(BASE_DIR, "vton"))

# Initialize database
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True, # Needed for cookies/auth headers in some cases
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session Middleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY, https_only=False)

# Register API routers
from app.routes import upload, tryon, result, auth, users, images, admin
app.include_router(upload.router)
app.include_router(tryon.router)
app.include_router(result.router)
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(images.router)
app.include_router(admin.router)

# Mount static files
# This must be mounted *after* the API routers
# The html=True argument makes it serve index.html for sub-paths that don't match a file
# This is ideal for single-page applications.
app.mount("/", StaticFiles(directory="public", html=True), name="public")