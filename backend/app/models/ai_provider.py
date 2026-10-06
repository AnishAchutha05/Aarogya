"""AI provider credential model - encrypted API keys."""

import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class AIProviderCredential(Base, TimestampMixin):
    """
    Stores user-owned AI provider API keys.
    - Keys are ALWAYS stored encrypted.
    - Raw keys are NEVER logged or returned to the frontend.
    - Only one active provider per user (enforced at service level).
    """

    __tablename__ = "ai_provider_credentials"
    __table_args__ = (
        UniqueConstraint("user_id", "provider", name="uq_user_provider"),
        Index("ix_ai_credentials_user_id", "user_id"),
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
        doc="gemini | openai | anthropic",
    )

    # Fernet-encrypted API key - NEVER store plaintext
    encrypted_api_key: Mapped[str] = mapped_column(
        String(2000),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        doc="The user's currently selected provider",
    )

    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
        doc="Has the key been successfully tested against the provider?",
    )

    user: Mapped["User"] = relationship("User", back_populates="ai_provider_credentials")


from app.models.user import User  # noqa: E402
