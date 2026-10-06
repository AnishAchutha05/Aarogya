from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date, datetime


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProfileUpdate(BaseModel):
    dob: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    nationality: Optional[str] = None
    region: Optional[str] = None
    dietary_preferences: Optional[list[str]] = None
    commonly_eaten_foods: Optional[list[str]] = None
    lifestyle_info: Optional[dict] = None
    activity_level: Optional[str] = None
    timezone: Optional[str] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    dob: Optional[date] = None
    gender: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    nationality: Optional[str] = None
    region: Optional[str] = None
    dietary_preferences: Optional[str] = None  # JSON string
    commonly_eaten_foods: Optional[str] = None # JSON string
    lifestyle_info: Optional[str] = None       # JSON string
    activity_level: Optional[str] = None
    timezone: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
