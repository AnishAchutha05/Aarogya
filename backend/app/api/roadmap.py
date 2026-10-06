"""Roadmap generation API routes."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.coach import RoadmapResponse
from app.services.coach_service import coach_service

router = APIRouter(prefix="/roadmap", tags=["roadmap"])


@router.post("/from-session/{session_id}", response_model=RoadmapResponse)
async def generate_roadmap_from_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Analyze an existing chat session and generate a structured markdown roadmap.
    Roadmap is not permanently stored, just returned.
    """
    markdown = await coach_service.generate_roadmap(db, current_user.id, session_id)
    return {"markdown": markdown}
