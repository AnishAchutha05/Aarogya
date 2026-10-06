"""User profile model."""

import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Profile(Base, TimestampMixin):
    __tablename__ = "profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    dob: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    gender: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    height_cm: Mapped[float | None] = mapped_column(nullable=True)
    weight_kg: Mapped[float | None] = mapped_column(nullable=True)

    nationality: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    region: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # JSON-compatible text fields (stored as plain text/JSON string)
    dietary_preferences: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="JSON array of dietary preferences/restrictions",
    )

    commonly_eaten_foods: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="JSON array of foods the user commonly eats",
    )

    lifestyle_info: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        doc="JSON object with lifestyle/activity info",
    )

    activity_level: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        doc="sedentary | lightly_active | moderately_active | very_active | extra_active",
    )

    timezone: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    user: Mapped["User"] = relationship("User", back_populates="profile")


from app.models.user import User  # noqa: E402
