"""User and authentication-related models."""

import uuid

from sqlalchemy import Boolean, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    avatar_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)

    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,  # Null for pure OAuth users
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    # Relationships
    profile: Mapped["Profile"] = relationship(
        "Profile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    oauth_accounts: Mapped[list["OAuthAccount"]] = relationship(
        "OAuthAccount",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    wellness_goals: Mapped[list["WellnessGoal"]] = relationship(
        "WellnessGoal",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    activities: Mapped[list["Activity"]] = relationship(
        "Activity",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    activity_logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    check_ins: Mapped[list["CheckIn"]] = relationship(
        "CheckIn",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    plans: Mapped[list["Plan"]] = relationship(
        "Plan",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    insights: Mapped[list["Insight"]] = relationship(
        "Insight",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    memory_records: Mapped[list["MemoryRecord"]] = relationship(
        "MemoryRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    ai_provider_credentials: Mapped[list["AIProviderCredential"]] = relationship(
        "AIProviderCredential",
        back_populates="user",
        cascade="all, delete-orphan",
    )

    progress_photos: Mapped[list["ProgressPhoto"]] = relationship(
        "ProgressPhoto",
        back_populates="user",
        cascade="all, delete-orphan",
    )


# Import related models here to enable forward refs
from app.models.profile import Profile  # noqa: E402
from app.models.auth import OAuthAccount, RefreshToken  # noqa: E402
from app.models.wellness import WellnessGoal, Activity, ActivityLog, CheckIn, Insight  # noqa: E402
from app.models.plan import Plan  # noqa: E402
from app.models.conversation import ChatSession  # noqa: E402
from app.models.memory import MemoryRecord  # noqa: E402
from app.models.ai_provider import AIProviderCredential  # noqa: E402
from app.models.photo import ProgressPhoto  # noqa: E402
