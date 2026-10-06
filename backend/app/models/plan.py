"""Plan and plan item models."""

import uuid
from datetime import date

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class Plan(Base, TimestampMixin):
    __tablename__ = "plans"
    __table_args__ = (Index("ix_plans_user_id", "user_id"),)

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

    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    end_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default="true"
    )

    user: Mapped["User"] = relationship("User", back_populates="plans")
    items: Mapped[list["PlanItem"]] = relationship(
        "PlanItem", back_populates="plan", cascade="all, delete-orphan"
    )


class PlanItem(Base, TimestampMixin):
    __tablename__ = "plan_items"
    __table_args__ = (Index("ix_plan_items_plan_id", "plan_id"),)

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )

    plan_id: Mapped[str] = mapped_column(
        ForeignKey("plans.id", ondelete="CASCADE"),
        nullable=False,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    item_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        doc="exercise | nutrition | habit | meditation | other",
    )

    day_of_week: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="0=Monday ... 6=Sunday",
    )

    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    completed_at: Mapped[date | None] = mapped_column(Date, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    plan: Mapped["Plan"] = relationship("Plan", back_populates="items")


from app.models.user import User  # noqa: E402
