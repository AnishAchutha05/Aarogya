"""Plan and plan item service."""

import logging
import uuid
from datetime import date
from typing import Optional

from sqlalchemy.orm import Session

from app.core.errors import ForbiddenError, NotFoundError
from app.models.plan import Plan, PlanItem

logger = logging.getLogger(__name__)


class PlanService:

    def create_plan(
        self,
        db: Session,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Plan:
        plan = Plan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
        )
        db.add(plan)
        db.commit()
        db.refresh(plan)
        return plan

    def list_plans(self, db: Session, user_id: str) -> list[Plan]:
        return (
            db.query(Plan)
            .filter(Plan.user_id == user_id)
            .order_by(Plan.created_at.desc())
            .all()
        )

    def get_plan(self, db: Session, plan_id: str, user_id: str) -> Plan:
        plan = db.get(Plan, plan_id)
        if not plan:
            raise NotFoundError("Plan")
        if plan.user_id != user_id:
            raise ForbiddenError()
        return plan

    def delete_plan(self, db: Session, plan_id: str, user_id: str) -> None:
        plan = self.get_plan(db, plan_id, user_id)
        db.delete(plan)
        db.commit()

    def add_plan_item(
        self,
        db: Session,
        plan_id: str,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        item_type: Optional[str] = None,
        day_of_week: Optional[int] = None,
        duration_minutes: Optional[int] = None,
        sort_order: int = 0,
    ) -> PlanItem:
        self.get_plan(db, plan_id, user_id)  # Ownership check

        item = PlanItem(
            id=str(uuid.uuid4()),
            plan_id=plan_id,
            title=title,
            description=description,
            item_type=item_type,
            day_of_week=day_of_week,
            duration_minutes=duration_minutes,
            sort_order=sort_order,
        )
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

    def complete_plan_item(
        self, db: Session, item_id: str, plan_id: str, user_id: str
    ) -> PlanItem:
        plan = self.get_plan(db, plan_id, user_id)
        item = db.get(PlanItem, item_id)
        if not item or item.plan_id != plan_id:
            raise NotFoundError("Plan item")
        item.is_completed = True
        item.completed_at = date.today()
        db.commit()
        db.refresh(item)
        return item


plan_service = PlanService()
