"""Users API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.user import ProfileResponse, ProfileUpdate, UserResponse
from app.services.user_service import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/me/profile", response_model=ProfileResponse)
def get_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return user_service.get_profile(db, current_user.id)


@router.put("/me/profile", response_model=ProfileResponse)
def update_profile(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return user_service.upsert_profile(
        db,
        current_user.id,
        dob=data.dob,
        gender=data.gender,
        height_cm=data.height_cm,
        weight_kg=data.weight_kg,
        nationality=data.nationality,
        region=data.region,
        dietary_preferences=data.dietary_preferences,
        commonly_eaten_foods=data.commonly_eaten_foods,
        lifestyle_info=data.lifestyle_info,
        activity_level=data.activity_level,
        timezone=data.timezone,
    )
