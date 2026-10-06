"""
Models package - import ALL models here so SQLAlchemy metadata is complete.
Alembic env.py imports from this module.
"""

# Import Base first
from app.models.base import Base, TimestampMixin  # noqa: F401

# Import all models in dependency order
from app.models.user import User  # noqa: F401
from app.models.auth import OAuthAccount, RefreshToken  # noqa: F401
from app.models.profile import Profile  # noqa: F401
from app.models.wellness import (  # noqa: F401
    WellnessGoal,
    Activity,
    ActivityLog,
    CheckIn,
    Insight,
)
from app.models.plan import Plan, PlanItem  # noqa: F401
from app.models.conversation import ChatSession, ChatMessage  # noqa: F401
from app.models.memory import MemoryRecord  # noqa: F401
from app.models.ai_provider import AIProviderCredential  # noqa: F401
from app.models.photo import ProgressPhoto  # noqa: F401

__all__ = [
    "Base",
    "TimestampMixin",
    "User",
    "OAuthAccount",
    "RefreshToken",
    "Profile",
    "WellnessGoal",
    "Activity",
    "ActivityLog",
    "CheckIn",
    "Insight",
    "Plan",
    "PlanItem",
    "ChatSession",
    "ChatMessage",
    "MemoryRecord",
    "AIProviderCredential",
    "ProgressPhoto",
]
