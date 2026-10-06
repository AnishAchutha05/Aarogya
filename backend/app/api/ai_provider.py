"""AI provider API routes."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.ai_provider import (
    ProviderCreate,
    ProviderResponse,
    ProviderSetActive,
    ProviderTestRequest,
    ProviderTestResponse,
)
from app.services.ai_provider_service import ai_provider_service

router = APIRouter(prefix="/ai-provider", tags=["ai-provider"])


@router.post("/test", response_model=ProviderTestResponse)
async def test_provider(
    data: ProviderTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return await ai_provider_service.verify_credential(db, current_user.id, data.provider)


@router.post("", response_model=ProviderResponse)
def add_provider(
    data: ProviderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return ai_provider_service.add_or_replace_credential(
        db, current_user.id, data.provider, data.api_key
    )


@router.get("", response_model=list[ProviderResponse])
def list_providers(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return ai_provider_service.list_credentials(db, current_user.id)


@router.post("/active", response_model=ProviderResponse)
def set_active_provider(
    data: ProviderSetActive,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return ai_provider_service.set_active_provider(db, current_user.id, data.provider)


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
def remove_provider(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    ai_provider_service.remove_credential(db, current_user.id, provider)
