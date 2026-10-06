"""Memory service for user-specific persistent memory."""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.memory import MemoryRecord

logger = logging.getLogger(__name__)


class MemoryService:

    def add_memory(
        self,
        db: Session,
        user_id: str,
        content: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
        qdrant_id: Optional[str] = None,
    ) -> MemoryRecord:
        record = MemoryRecord(
            id=str(uuid.uuid4()),
            user_id=user_id,
            content=content,
            category=category,
            source=source,
            qdrant_id=qdrant_id,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    def get_user_memories(
        self,
        db: Session,
        user_id: str,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> list[MemoryRecord]:
        q = db.query(MemoryRecord).filter(
            MemoryRecord.user_id == user_id,
            MemoryRecord.is_active == True,  # noqa: E712
        )
        if category:
            q = q.filter(MemoryRecord.category == category)
        return q.order_by(MemoryRecord.created_at.desc()).limit(limit).all()

    def deactivate_memory(
        self, db: Session, memory_id: str, user_id: str
    ) -> None:
        record = db.get(MemoryRecord, memory_id)
        if not record:
            raise NotFoundError("Memory record")
        if record.user_id != user_id:
            raise ForbiddenError()
        record.is_active = False
        db.commit()


memory_service = MemoryService()
