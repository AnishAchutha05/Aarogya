"""User memory record model."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class MemoryRecord(Base, TimestampMixin):
    """
    Stores important persistent memory for a user.
    Short-term: current chat history (in ChatMessage).
    Persistent: key user facts, preferences, important past events.
    These may be vectorized in Qdrant for semantic retrieval,
    but PostgreSQL remains the source of truth.
    """

    __tablename__ = "memory_records"
    __table_args__ = (
        Index("ix_memory_records_user_id", "user_id"),
        Index("ix_memory_records_category", "category"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="preference | goal | event | feedback | other",
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        doc="The memory content - what Aaryu should remember about this user",
    )

    # Optional: Qdrant vector ID for semantic retrieval linkback
    qdrant_id: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        doc="UUID used as point ID in Qdrant user_memory collection",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="Soft delete / deactivate old memories",
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="conversation | checkin | profile | manual",
    )

    user: Mapped["User"] = relationship("User", back_populates="memory_records")


from app.models.user import User  # noqa: E402
