"""OAuth accounts and refresh token models."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class OAuthAccount(Base, TimestampMixin):
    """Maps an OAuth provider account to a platform user."""

    __tablename__ = "oauth_accounts"
    __table_args__ = (
        UniqueConstraint("provider", "provider_user_id", name="uq_oauth_provider_user"),
        Index("ix_oauth_user_id", "user_id"),
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

    provider: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    provider_email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Retained for backwards-compatible schema/data only; current OAuth flow
    # does not persist provider access or refresh tokens.
    access_token: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    refresh_token: Mapped[str | None] = mapped_column(String(2000), nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="oauth_accounts")


class RefreshToken(Base, TimestampMixin):
    """Hashed refresh token records for rotation-based auth."""

    __tablename__ = "refresh_tokens"
    __table_args__ = (
        Index("ix_refresh_token_user_id", "user_id"),
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

    # Stored hashed - never store raw token
    token_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
        index=True,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    revoked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    family: Mapped[str | None] = mapped_column(
        String(36),
        nullable=True,
        index=True,
        doc="Token family for rotation - revoke whole family on reuse detection",
    )

    rotated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    rotation_successor_id: Mapped[str | None] = mapped_column(String(36), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="refresh_tokens")


from app.models.user import User  # noqa: E402
