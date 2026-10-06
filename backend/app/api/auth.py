"""Auth API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.core.errors import ConflictError
from app.core.security import get_current_active_user
from app.models.user import User
from app.schemas.auth import (
    ChangePassword,
    TokenRefresh,
    TokenResponse,
    UserLogin,
    UserRegister,
)
from app.schemas.user import UserResponse
from app.services.auth_service import auth_service
from app.services.oauth_service import oauth_service

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)

REFRESH_COOKIE_NAME = "aarogya_refresh"


def _set_refresh_cookie(response: Response, request: Request, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/auth",
    )


def _clear_refresh_cookie(response: Response, request: Request) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        path="/auth",
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(data: UserRegister, db: Session = Depends(get_db)):
    user = auth_service.register(db, data.email, data.password, data.name)
    return user


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    _, access, refresh = auth_service.login(db, data.email, data.password)
    _set_refresh_cookie(response, request, refresh)
    return {"access_token": access, "refresh_token": refresh}


@router.post("/refresh", response_model=TokenResponse)
def refresh(data: TokenRefresh, request: Request, response: Response, db: Session = Depends(get_db)):
    raw_token = data.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if not raw_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    new_access, new_refresh = auth_service.refresh_session(db, raw_token)
    _set_refresh_cookie(response, request, new_refresh)
    return {"access_token": new_access, "refresh_token": new_refresh}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(data: TokenRefresh, request: Request, db: Session = Depends(get_db)):
    raw_token = data.refresh_token or request.cookies.get(REFRESH_COOKIE_NAME)
    if raw_token:
        auth_service.logout(db, raw_token)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    _clear_refresh_cookie(response, request)
    return response


@router.get("/google")
def google_login():
    return _oauth_redirect("google")


@router.get("/google/callback")
async def google_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    return await _oauth_callback("google", request, db)


@router.get("/google/link")
def google_link(current_user: User = Depends(get_current_active_user)):
    return _oauth_redirect("google", link_user_id=current_user.id)


@router.get("/yahoo")
def yahoo_login():
    return _oauth_redirect("yahoo")


@router.get("/yahoo/callback")
async def yahoo_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    return await _oauth_callback("yahoo", request, db)


@router.get("/yahoo/link")
def yahoo_link(current_user: User = Depends(get_current_active_user)):
    return _oauth_redirect("yahoo", link_user_id=current_user.id)


def _oauth_redirect(provider: str, link_user_id: str | None = None) -> RedirectResponse:
    try:
        return RedirectResponse(
            oauth_service.authorization_url(provider, link_user_id=link_user_id),
            status_code=302,
        )
    except RuntimeError as exc:
        if "not configured" in str(exc):
            raise HTTPException(status_code=503, detail="OAuth provider is not configured") from None
        raise HTTPException(status_code=503, detail="OAuth authorization is unavailable") from None


async def _oauth_callback(provider: str, request: Request, db: Session) -> RedirectResponse:
    if request.query_params.get("error"):
        raise HTTPException(status_code=400, detail="OAuth authorization was denied")
    try:
        identity = await oauth_service.exchange_and_validate(
            provider,
            request.query_params.get("code", ""),
            request.query_params.get("state", ""),
        )
        link_user_id = identity.pop("link_user_id", None)
        if link_user_id:
            linking_user = db.get(User, link_user_id)
            if not linking_user or not linking_user.is_active:
                raise HTTPException(status_code=401, detail="Linking session is no longer valid")
            auth_service.link_oauth_identity(
                db,
                linking_user,
                provider=provider,
                provider_user_id=identity["provider_user_id"],
                email=identity["email"],
                avatar_url=identity.get("avatar_url"),
            )
            return RedirectResponse(
                f"{settings.FRONTEND_URL.rstrip('/')}/login#oauth=linked",
                status_code=303,
            )

        user = auth_service.get_or_create_oauth_user(
            db,
            provider=provider,
            provider_user_id=identity["provider_user_id"],
            email=identity["email"],
            name=identity.get("name"),
            avatar_url=identity.get("avatar_url"),
        )
        access, refresh_token = auth_service.create_session(db, user)
    except HTTPException:
        raise
    except Exception as exc:
        logger.warning("OAuth callback rejected provider=%s error=%s", provider, type(exc).__name__)
        if isinstance(exc, (ValueError, ConflictError)):
            raise HTTPException(status_code=400, detail=str(exc)) from None
        raise HTTPException(status_code=502, detail="OAuth sign-in could not be completed") from None

    redirect = RedirectResponse(
        f"{settings.FRONTEND_URL.rstrip('/')}/login#access_token={access}&token_type=bearer",
        status_code=303,
    )
    _set_refresh_cookie(redirect, request, refresh_token)
    return redirect


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
def change_password(
    data: ChangePassword,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    auth_service.change_password(
        db, current_user, data.old_password, data.new_password
    )
