from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class PlanItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    item_type: Optional[str] = None
    day_of_week: Optional[int] = None
    duration_minutes: Optional[int] = None
    sort_order: int = 0


class PlanItemResponse(BaseModel):
    id: str
    plan_id: str
    title: str
    description: Optional[str] = None
    item_type: Optional[str] = None
    day_of_week: Optional[int] = None
    duration_minutes: Optional[int] = None
    is_completed: bool
    completed_at: Optional[date] = None
    sort_order: int
    created_at: datetime

    class Config:
        from_attributes = True


class PlanCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class PlanResponse(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    is_active: bool
    created_at: datetime
    items: list[PlanItemResponse] = []

    class Config:
        from_attributes = True
