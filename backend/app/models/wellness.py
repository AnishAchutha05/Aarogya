"""Wellness domain models: goals, activities, check-ins, insights."""

import uuid
from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class WellnessGoal(Base, TimestampMixin):
    __tablename__ = "wellness_goals"
    __table_args__ = (Index("ix_wellness_goals_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="weight_loss | fitness | nutrition | mental_health | sleep | general",
    )

    target_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    target_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    current_value: Mapped[float | None] = mapped_column(Float, nullable=True)

    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    user: Mapped["User"] = relationship("User", back_populates="wellness_goals")


class Activity(Base, TimestampMixin):
    """A type of wellness activity available to a user."""

    __tablename__ = "activities"
    __table_args__ = (Index("ix_activities_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="exercise | nutrition | meditation | sleep | habit",
    )

    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    user: Mapped["User"] = relationship("User", back_populates="activities")
    logs: Mapped[list["ActivityLog"]] = relationship(
        "ActivityLog", back_populates="activity", cascade="all, delete-orphan"
    )


class ActivityLog(Base, TimestampMixin):
    """Records a user completing an activity."""

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_user_id", "user_id"),
        Index("ix_activity_logs_activity_id", "activity_id"),
        Index("ix_activity_logs_logged_date", "logged_date"),
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

    activity_id: Mapped[str] = mapped_column(
        ForeignKey("activities.id", ondelete="CASCADE"),
        nullable=False,
    )

    logged_date: Mapped[date] = mapped_column(Date, nullable=False)

    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    intensity: Mapped[str | None] = mapped_column(String(50), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="activity_logs")
    activity: Mapped["Activity"] = relationship("Activity", back_populates="logs")


class CheckIn(Base, TimestampMixin):
    """Daily wellness check-in record."""

    __tablename__ = "check_ins"
    __table_args__ = (
        UniqueConstraint("user_id", "check_in_date", name="uq_checkin_user_date"),
        Index("ix_check_ins_user_id", "user_id"),
        Index("ix_check_ins_date", "check_in_date"),
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

    check_in_date: Mapped[date] = mapped_column(Date, nullable=False)

    mood_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="1-10 scale",
    )

    energy_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="1-10 scale",
    )

    sleep_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    water_intake_ml: Mapped[float | None] = mapped_column(Float, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    symptoms: Mapped[str | None] = mapped_column(Text, nullable=True, doc="JSON array")
    stress_score: Mapped[int | None] = mapped_column(Integer, nullable=True, doc="1-10")

    user: Mapped["User"] = relationship("User", back_populates="check_ins")


class Insight(Base, TimestampMixin):
    """AI/system-generated wellness insight for a user."""

    __tablename__ = "insights"
    __table_args__ = (Index("ix_insights_user_id", "user_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="system | ai | check_in",
    )

    user: Mapped["User"] = relationship("User", back_populates="insights")


from app.models.user import User  # noqa: E402
