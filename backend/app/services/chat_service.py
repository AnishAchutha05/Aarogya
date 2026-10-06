"""Chat session and message service."""

import logging
import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.conversation import ChatMessage, ChatSession

logger = logging.getLogger(__name__)


class ChatService:

    def create_session(
        self, db: Session, user_id: str, title: Optional[str] = None
    ) -> ChatSession:
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title or "New Conversation",
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def list_sessions(self, db: Session, user_id: str) -> list[ChatSession]:
        return (
            db.query(ChatSession)
            .filter(
                ChatSession.user_id == user_id,
                ChatSession.is_active == True,  # noqa: E712
            )
            .order_by(ChatSession.created_at.desc())
            .all()
        )

    def get_session(
        self, db: Session, session_id: str, user_id: str
    ) -> ChatSession:
        session = db.get(ChatSession, session_id)
        if not session:
            raise NotFoundError("Chat session")
        if session.user_id != user_id:
            raise ForbiddenError()
        return session

    def delete_session(
        self, db: Session, session_id: str, user_id: str
    ) -> None:
        session = self.get_session(db, session_id, user_id)
        session.is_active = False  # Soft delete
        db.commit()

    def add_message(
        self,
        db: Session,
        session_id: str,
        user_id: str,
        role: str,
        content: str,
        token_count: Optional[int] = None,
        metadata_json: Optional[str] = None,
    ) -> ChatMessage:
        # Verify session ownership
        self.get_session(db, session_id, user_id)

        message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            role=role,
            content=content,
            token_count=token_count,
            metadata_json=metadata_json,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message

    def get_messages(
        self, db: Session, session_id: str, user_id: str, limit: int = 100
    ) -> list[ChatMessage]:
        self.get_session(db, session_id, user_id)
        return (
            db.query(ChatMessage)
            .filter(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
            .limit(limit)
            .all()
        )


chat_service = ChatService()
