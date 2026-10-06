from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class GoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    target_date: Optional[date] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    current_value: Optional[float] = None
    target_date: Optional[date] = None
    is_active: Optional[bool] = None
    is_completed: Optional[bool] = None


class GoalResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    target_unit: Optional[str] = None
    current_value: Optional[float] = None
    target_date: Optional[date] = None
    is_active: bool
    is_completed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ActivityCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None


class ActivityResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    duration_minutes: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ActivityLogCreate(BaseModel):
    activity_id: str
    logged_date: date
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    intensity: Optional[str] = None


class ActivityLogResponse(BaseModel):
    id: str
    activity_id: str
    logged_date: date
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None
    intensity: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CheckInCreate(BaseModel):
    check_in_date: date
    mood_score: Optional[int] = None
    energy_score: Optional[int] = None
    sleep_hours: Optional[float] = None
    water_intake_ml: Optional[float] = None
    notes: Optional[str] = None
    stress_score: Optional[int] = None


class CheckInResponse(BaseModel):
    id: str
    check_in_date: date
    mood_score: Optional[int] = None
    energy_score: Optional[int] = None
    sleep_hours: Optional[float] = None
    water_intake_ml: Optional[float] = None
    notes: Optional[str] = None
    stress_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class InsightResponse(BaseModel):
    id: str
    category: Optional[str] = None
    title: str
    content: str
    is_read: bool
    source: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
