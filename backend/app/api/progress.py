"""Progress API routes (Check-ins)."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.wellness import CheckInCreate, CheckInResponse
from app.services.wellness_service import wellness_service

router = APIRouter(prefix="/progress", tags=["progress"])

@router.post("/check-in", response_model=CheckInResponse)
def check_in(data: CheckInCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.create_or_update_checkin(db, current_user.id, **data.model_dump())

@router.get("/check-ins", response_model=list[CheckInResponse])
def get_recent_checkins(limit: int = 7, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return wellness_service.get_recent_checkins(db, current_user.id, limit)
