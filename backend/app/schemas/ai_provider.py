from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ProviderCreate(BaseModel):
    provider: str
    api_key: str


class ProviderResponse(BaseModel):
    id: str
    provider: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProviderSetActive(BaseModel):
    provider: str


class ProviderTestRequest(BaseModel):
    provider: Optional[str] = None


class ProviderTestResponse(BaseModel):
    provider: str
    configured: bool
    verified: bool
