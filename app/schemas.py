from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Base schema for a User
class UserBase(BaseModel):
    email: str
    name: Optional[str] = None
    profile_image: Optional[str] = None

# Schema for creating a user (if you had a direct creation endpoint)
class UserCreate(UserBase):
    pass

# Schema for updating a user
class UserUpdate(BaseModel):
    name: Optional[str] = None

# Schema for admin updating a user
class AdminUserUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

# Schema for reading/returning a user from the API
class User(UserBase):
    id: int
    google_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True # orm_mode = True for Pydantic v1

# Generic schema for returning any photo type
class Photo(BaseModel):
    id: int
    filename: str
    user_id: int
    uploaded_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schema for JWT token
class Token(BaseModel):
    access_token: str
    token_type: str
