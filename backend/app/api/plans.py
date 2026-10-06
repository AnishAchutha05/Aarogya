"""Plans API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.plan import PlanCreate, PlanItemCreate, PlanItemResponse, PlanResponse
from app.services.plan_service import plan_service

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(data: PlanCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return plan_service.create_plan(db, current_user.id, **data.model_dump())


@router.get("", response_model=list[PlanResponse])
def list_plans(db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return plan_service.list_plans(db, current_user.id)


@router.get("/{plan_id}", response_model=PlanResponse)
def get_plan(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return plan_service.get_plan(db, plan_id, current_user.id)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    plan_service.delete_plan(db, plan_id, current_user.id)


@router.post("/{plan_id}/items", response_model=PlanItemResponse, status_code=status.HTTP_201_CREATED)
def add_plan_item(plan_id: str, data: PlanItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return plan_service.add_plan_item(db, plan_id, current_user.id, **data.model_dump())


@router.post("/{plan_id}/items/{item_id}/complete", response_model=PlanItemResponse)
def complete_plan_item(plan_id: str, item_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    return plan_service.complete_plan_item(db, item_id, plan_id, current_user.id)
