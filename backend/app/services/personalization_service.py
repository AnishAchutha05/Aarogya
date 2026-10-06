"""Personalization service - deterministic recommendations."""

import json
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.profile import Profile
from app.models.wellness import Activity, ActivityLog, CheckIn, WellnessGoal

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Deterministic personalization logic.
    Recommendations are based on structured data, NOT LLM outputs.
    LLM can explain recommendations; this service generates them.
    """

    def get_user_context(self, db: Session, user_id: str) -> dict:
        """
        Build a safe context dict for Aaryu.
        Only returns non-sensitive user data for AI context injection.
        """
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        goals = (
            db.query(WellnessGoal)
            .filter(
                WellnessGoal.user_id == user_id,
                WellnessGoal.is_active == True,  # noqa: E712
            )
            .all()
        )

        recent_checkins = (
            db.query(CheckIn)
            .filter(CheckIn.user_id == user_id)
            .order_by(CheckIn.check_in_date.desc())
            .limit(7)
            .all()
        )

        recent_activity = (
            db.query(ActivityLog)
            .filter(ActivityLog.user_id == user_id)
            .order_by(ActivityLog.logged_date.desc())
            .limit(10)
            .all()
        )

        context = {
            "profile": {},
            "goals": [],
            "recent_checkins": [],
            "recent_activity": [],
        }

        if profile:
            age = None
            if profile.dob:
                today = date.today()
                age = today.year - profile.dob.year - (
                    (today.month, today.day) < (profile.dob.month, profile.dob.day)
                )
            context["profile"] = {
                "age": age,
                "gender": profile.gender,
                "height_cm": profile.height_cm,
                "weight_kg": profile.weight_kg,
                "nationality": profile.nationality,
                "region": profile.region,
                "activity_level": profile.activity_level,
                "dietary_preferences": json.loads(profile.dietary_preferences)
                if profile.dietary_preferences
                else [],
                "commonly_eaten_foods": json.loads(profile.commonly_eaten_foods)
                if profile.commonly_eaten_foods
                else [],
            }

        context["goals"] = [
            {
                "title": g.title,
                "category": g.category,
                "target_value": g.target_value,
                "target_unit": g.target_unit,
                "current_value": g.current_value,
            }
            for g in goals
        ]

        context["recent_checkins"] = [
            {
                "date": str(c.check_in_date),
                "mood_score": c.mood_score,
                "energy_score": c.energy_score,
                "sleep_hours": c.sleep_hours,
                "stress_score": c.stress_score,
            }
            for c in recent_checkins
        ]

        context["recent_activity"] = [
            {
                "date": str(a.logged_date),
                "duration_minutes": a.duration_minutes,
                "intensity": a.intensity,
            }
            for a in recent_activity
        ]

        return context

    def recommend_activities(
        self, db: Session, user_id: str, available_minutes: Optional[int] = None
    ) -> list[Activity]:
        """
        Deterministic activity recommendation.
        Filters by available_minutes if provided.
        Prioritizes activities not done recently.
        """
        activities = (
            db.query(Activity)
            .filter(
                Activity.user_id == user_id,
                Activity.is_active == True,  # noqa: E712
            )
            .all()
        )

        if available_minutes:
            activities = [
                a for a in activities
                if a.duration_minutes is None or a.duration_minutes <= available_minutes
            ]

        # Deprioritize recently completed
        cutoff = date.today() - timedelta(days=3)
        recent_ids = {
            log.activity_id
            for log in db.query(ActivityLog)
            .filter(
                ActivityLog.user_id == user_id,
                ActivityLog.logged_date >= cutoff,
            )
            .all()
        }

        not_recent = [a for a in activities if a.id not in recent_ids]
        recent = [a for a in activities if a.id in recent_ids]

        return not_recent + recent


personalization_service = PersonalizationService()
