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

# Schema for reading/returning a user from the API
class User(UserBase):
    id: int
    google_id: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True # orm_mode = True for Pydantic v1
