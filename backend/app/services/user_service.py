"""User and profile business logic service."""

import json
import logging
import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import NotFoundError
from app.models.profile import Profile
from app.models.user import User

logger = logging.getLogger(__name__)


class UserService:

    def get_user(self, db: Session, user_id: str) -> User:
        user = db.get(User, user_id)
        if not user:
            raise NotFoundError("User")
        return user

    def get_profile(self, db: Session, user_id: str) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            raise NotFoundError("Profile")
        return profile

    def upsert_profile(
        self,
        db: Session,
        user_id: str,
        *,
        dob: Optional[date] = None,
        gender: Optional[str] = None,
        height_cm: Optional[float] = None,
        weight_kg: Optional[float] = None,
        nationality: Optional[str] = None,
        region: Optional[str] = None,
        dietary_preferences: Optional[list] = None,
        commonly_eaten_foods: Optional[list] = None,
        lifestyle_info: Optional[dict] = None,
        activity_level: Optional[str] = None,
        timezone: Optional[str] = None,
    ) -> Profile:
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            profile = Profile(id=str(uuid.uuid4()), user_id=user_id)
            db.add(profile)

        if dob is not None:
            profile.dob = dob
        if gender is not None:
            profile.gender = gender
        if height_cm is not None:
            profile.height_cm = height_cm
        if weight_kg is not None:
            profile.weight_kg = weight_kg
        if nationality is not None:
            profile.nationality = nationality
        if region is not None:
            profile.region = region
        if dietary_preferences is not None:
            profile.dietary_preferences = json.dumps(dietary_preferences)
        if commonly_eaten_foods is not None:
            profile.commonly_eaten_foods = json.dumps(commonly_eaten_foods)
        if lifestyle_info is not None:
            profile.lifestyle_info = json.dumps(lifestyle_info)
        if activity_level is not None:
            profile.activity_level = activity_level
        if timezone is not None:
            profile.timezone = timezone

        db.commit()
        db.refresh(profile)
        return profile

    def update_user_name(self, db: Session, user: User, name: str) -> User:
        user.name = name
        db.commit()
        db.refresh(user)
        return user


user_service = UserService()
