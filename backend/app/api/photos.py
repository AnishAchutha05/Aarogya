"""Photos API routes."""

from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.photo import PhotoResponse
from app.services.photo_service import photo_service

router = APIRouter(prefix="/photos", tags=["photos"])


@router.post("", response_model=PhotoResponse, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    file: UploadFile = File(...),
    photo_date: Optional[date] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await photo_service.upload_photo(
        db, current_user.id, file, photo_date, notes
    )


@router.get("", response_model=list[PhotoResponse])
def list_photos(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return photo_service.list_photos(db, current_user.id)


@router.delete("/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_photo(photo_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    photo_service.delete_photo(db, photo_id, current_user.id)


@router.get("/{photo_id}/file")
def get_photo_file(photo_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    file_path = photo_service.get_file_path(db, photo_id, current_user.id)
    return FileResponse(file_path)
