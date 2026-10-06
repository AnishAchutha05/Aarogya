"""Wellness API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.wellness import (
    ActivityCreate,
    ActivityLogCreate,
    ActivityLogResponse,
    ActivityResponse,
    GoalCreate,
    GoalResponse,
    GoalUpdate,
    InsightResponse,
)
from app.services.wellness_service import wellness_service

router = APIRouter(prefix="/wellness", tags=["wellness"])

# Goals
@router.post("/goals", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(data: GoalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.create_goal(db, current_user.id, **data.model_dump())

@router.get("/goals", response_model=list[GoalResponse])
def list_goals(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.list_goals(db, current_user.id)

@router.get("/goals/{goal_id}", response_model=GoalResponse)
def get_goal(goal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.get_goal(db, goal_id, current_user.id)

@router.put("/goals/{goal_id}", response_model=GoalResponse)
def update_goal(goal_id: str, data: GoalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.update_goal(db, goal_id, current_user.id, **data.model_dump(exclude_unset=True))

@router.delete("/goals/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(goal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    wellness_service.delete_goal(db, goal_id, current_user.id)

# Activities
@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
def create_activity(data: ActivityCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.create_activity(db, current_user.id, **data.model_dump())

@router.get("/activities", response_model=list[ActivityResponse])
def list_activities(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.list_activities(db, current_user.id)

@router.post("/activities/log", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
def log_activity(data: ActivityLogCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.log_activity(db, current_user.id, **data.model_dump())

@router.get("/activities/history", response_model=list[ActivityLogResponse])
def get_activity_history(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.get_activity_history(db, current_user.id)

# Insights
@router.get("/insights", response_model=list[InsightResponse])
def get_insights(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.list_insights(db, current_user.id)
