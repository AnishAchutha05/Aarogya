"""Progress photo model."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class ProgressPhoto(Base, TimestampMixin):
    __tablename__ = "progress_photos"
    __table_args__ = (Index("ix_progress_photos_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Storage-agnostic: local path or object store key
    storage_key: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        doc="Relative path or object storage key - NOT an arbitrary user-controlled path",
    )

    original_filename: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        doc="Sanitized original filename for display only",
    )

    mime_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    file_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    photo_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        doc="The date the photo was taken (user-supplied)",
    )

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="progress_photos")


from app.models.user import User  # noqa: E402
