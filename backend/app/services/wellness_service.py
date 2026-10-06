"""Wellness domain service: goals, activities, check-ins, insights."""

import logging
import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.wellness import Activity, ActivityLog, CheckIn, Insight, WellnessGoal

logger = logging.getLogger(__name__)


class WellnessService:

    # ------------------------------------------------------------------ Goals

    def create_goal(
        self,
        db: Session,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        target_value: Optional[float] = None,
        target_unit: Optional[str] = None,
        target_date: Optional[date] = None,
    ) -> WellnessGoal:
        goal = WellnessGoal(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            category=category,
            target_value=target_value,
            target_unit=target_unit,
            target_date=target_date,
        )
        db.add(goal)
        db.commit()
        db.refresh(goal)
        return goal

    def list_goals(self, db: Session, user_id: str) -> list[WellnessGoal]:
        return (
            db.query(WellnessGoal)
            .filter(WellnessGoal.user_id == user_id)
            .order_by(WellnessGoal.created_at.desc())
            .all()
        )

    def get_goal(self, db: Session, goal_id: str, user_id: str) -> WellnessGoal:
        goal = db.get(WellnessGoal, goal_id)
        if not goal:
            raise NotFoundError("Goal")
        if goal.user_id != user_id:
            raise ForbiddenError()
        return goal

    def update_goal(
        self, db: Session, goal_id: str, user_id: str, **kwargs
    ) -> WellnessGoal:
        goal = self.get_goal(db, goal_id, user_id)
        allowed = {
            "title", "description", "category", "target_value",
            "target_unit", "current_value", "target_date", "is_active", "is_completed"
        }
        for k, v in kwargs.items():
            if k in allowed and v is not None:
                setattr(goal, k, v)
        db.commit()
        db.refresh(goal)
        return goal

    def delete_goal(self, db: Session, goal_id: str, user_id: str) -> None:
        goal = self.get_goal(db, goal_id, user_id)
        db.delete(goal)
        db.commit()

    # --------------------------------------------------------------- Activities

    def create_activity(
        self,
        db: Session,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        duration_minutes: Optional[int] = None,
    ) -> Activity:
        activity = Activity(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            description=description,
            category=category,
            duration_minutes=duration_minutes,
        )
        db.add(activity)
        db.commit()
        db.refresh(activity)
        return activity

    def list_activities(self, db: Session, user_id: str) -> list[Activity]:
        return (
            db.query(Activity)
            .filter(Activity.user_id == user_id, Activity.is_active == True)  # noqa: E712
            .order_by(Activity.name)
            .all()
        )

    def get_activity(self, db: Session, activity_id: str, user_id: str) -> Activity:
        activity = db.get(Activity, activity_id)
        if not activity:
            raise NotFoundError("Activity")
        if activity.user_id != user_id:
            raise ForbiddenError()
        return activity

    def log_activity(
        self,
        db: Session,
        user_id: str,
        activity_id: str,
        logged_date: date,
        duration_minutes: Optional[int] = None,
        notes: Optional[str] = None,
        intensity: Optional[str] = None,
    ) -> ActivityLog:
        # Validate ownership
        self.get_activity(db, activity_id, user_id)

        log = ActivityLog(
            id=str(uuid.uuid4()),
            user_id=user_id,
            activity_id=activity_id,
            logged_date=logged_date,
            duration_minutes=duration_minutes,
            notes=notes,
            intensity=intensity,
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    def get_activity_history(
        self,
        db: Session,
        user_id: str,
        limit: int = 50,
    ) -> list[ActivityLog]:
        return (
            db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.logged_date.desc())
            .limit(limit)
            .all()
        )

    # ----------------------------------------------------------- Check-ins

    def create_or_update_checkin(
        self,
        db: Session,
        user_id: str,
        check_in_date: date,
        mood_score: Optional[int] = None,
        energy_score: Optional[int] = None,
        sleep_hours: Optional[float] = None,
        water_intake_ml: Optional[float] = None,
        notes: Optional[str] = None,
        stress_score: Optional[int] = None,
    ) -> CheckIn:
        existing = (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user_id, CheckIn.check_in_date == check_in_date)
            .first()
        )

        if existing:
            if mood_score is not None:
                existing.mood_score = mood_score
            if energy_score is not None:
                existing.energy_score = energy_score
            if sleep_hours is not None:
                existing.sleep_hours = sleep_hours
            if water_intake_ml is not None:
                existing.water_intake_ml = water_intake_ml
            if notes is not None:
                existing.notes = notes
            if stress_score is not None:
                existing.stress_score = stress_score
            db.commit()
            db.refresh(existing)
            return existing

        checkin = CheckIn(
            id=str(uuid.uuid4()),
            user_id=user_id,
            check_in_date=check_in_date,
            mood_score=mood_score,
            energy_score=energy_score,
            sleep_hours=sleep_hours,
            water_intake_ml=water_intake_ml,
            notes=notes,
            stress_score=stress_score,
        )
        db.add(checkin)
        db.commit()
        db.refresh(checkin)
        return checkin

    def get_recent_checkins(
        self, db: Session, user_id: str, limit: int = 7
    ) -> list[CheckIn]:
        return (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user_id)
            .order_by(CheckIn.check_in_date.desc())
            .limit(limit)
            .all()
        )

    # ----------------------------------------------------------- Insights

    def create_insight(
        self,
        db: Session,
        user_id: str,
        title: str,
        content: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Insight:
        insight = Insight(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            content=content,
            category=category,
            source=source,
        )
        db.add(insight)
        db.commit()
        db.refresh(insight)
        return insight

    def list_insights(self, db: Session, user_id: str, limit: int = 20) -> list[Insight]:
        return (
            db.query(Insight)
            .filter(Insight.user_id == user_id)
            .order_by(Insight.created_at.desc())
            .limit(limit)
            .all()
        )


wellness_service = WellnessService()
