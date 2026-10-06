from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class PhotoResponse(BaseModel):
    id: str
    original_filename: Optional[str] = None
    mime_type: str
    file_size_bytes: Optional[int] = None
    photo_date: Optional[date] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
