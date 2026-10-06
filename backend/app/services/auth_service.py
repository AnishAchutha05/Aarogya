"""Authentication business logic service."""

import base64
import hashlib
import hmac
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ConflictError, ForbiddenError, NotFoundError
from app.core.security import (
    generate_refresh_token,
    generate_token_family,
    hash_password,
    hash_refresh_token,
    verify_password,
    create_access_token,
)
from app.models.auth import OAuthAccount, RefreshToken
from app.models.user import User

logger = logging.getLogger(__name__)


class AuthService:

    def register(self, db: Session, email: str, password: str, name: Optional[str] = None) -> User:
        """Register a new email/password user."""
        normalized_email = email.lower().strip()
        existing = db.query(User).filter(User.email == normalized_email).first()
        if existing:
            raise ConflictError("Email already registered")

        user = User(
            id=str(uuid.uuid4()),
            email=normalized_email,
            name=name,
            hashed_password=hash_password(password),
            is_active=True,
            is_verified=False,
        )
        db.add(user)
        db.flush()

        # Auto-create empty profile
        from app.models.profile import Profile
        profile = Profile(id=str(uuid.uuid4()), user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(user)

        logger.info("User registered: %s", user.id)
        return user

    def login(self, db: Session, email: str, password: str) -> tuple[User, str, str]:
        """
        Authenticate user and issue access + refresh tokens.
        Returns (user, access_token, refresh_token).
        """
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not user.hashed_password:
            raise ForbiddenError()
        if not verify_password(password, user.hashed_password):
            raise ForbiddenError()
        if not user.is_active:
            raise ForbiddenError()

        access_token = create_access_token(user.id)
        raw_refresh, refresh_token_record = self._issue_refresh_token(db, user.id)
        db.commit()

        logger.info("User logged in: %s", user.id)
        return user, access_token, raw_refresh

    def create_session(self, db: Session, user: User) -> tuple[str, str]:
        """Issue Aarogya access and refresh tokens for an authenticated user."""
        access_token = create_access_token(user.id)
        raw_refresh, _ = self._issue_refresh_token(db, user.id)
        db.commit()
        return access_token, raw_refresh

    def refresh_session(self, db: Session, raw_token: str) -> tuple[str, str]:
        """Rotate a refresh token, idempotently handling near-simultaneous retries."""
        token_hash = hash_refresh_token(raw_token)
        record = (
            db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .with_for_update()
            .first()
        )
        if not record:
            raise ForbiddenError()

        now = datetime.now(timezone.utc)
        if record.revoked:
            rotated_at = record.rotated_at
            if rotated_at and rotated_at.tzinfo is None:
                rotated_at = rotated_at.replace(tzinfo=timezone.utc)
            if (
                rotated_at
                and now - rotated_at <= timedelta(seconds=10)
                and record.rotation_successor_id
            ):
                successor = db.get(RefreshToken, record.rotation_successor_id)
                if successor and not successor.revoked:
                    successor_expiry = successor.expires_at
                    if successor_expiry.tzinfo is None:
                        successor_expiry = successor_expiry.replace(tzinfo=timezone.utc)
                    if successor_expiry > now:
                        return (
                            create_access_token(record.user_id),
                            self._derive_rotation_token(raw_token, successor.id),
                        )

            if record.family:
                db.query(RefreshToken).filter(
                    RefreshToken.family == record.family
                ).update({"revoked": True})
                db.commit()
            raise ForbiddenError()

        expires_at = record.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if expires_at < now:
            record.revoked = True
            db.commit()
            raise ForbiddenError()

        successor_id = str(uuid.uuid4())
        raw_successor = self._derive_rotation_token(raw_token, successor_id)
        successor = RefreshToken(
            id=successor_id,
            user_id=record.user_id,
            token_hash=hash_refresh_token(raw_successor),
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            family=record.family,
        )
        record.revoked = True
        record.rotated_at = now
        record.rotation_successor_id = successor_id
        db.add(successor)
        db.commit()
        return create_access_token(record.user_id), raw_successor

    @staticmethod
    def _derive_rotation_token(previous_token: str, successor_id: str) -> str:
        message = f"refresh-rotation:{successor_id}:{previous_token}".encode()
        digest = hmac.new(settings.JWT_SECRET.encode(), message, hashlib.sha512).digest()
        return base64.urlsafe_b64encode(digest).decode().rstrip("=")

    def logout(self, db: Session, raw_token: str) -> None:
        """Revoke a refresh token."""
        token_hash = hash_refresh_token(raw_token)
        record = (
            db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )
        if record:
            record.revoked = True
            db.commit()

    def change_password(
        self, db: Session, user: User, old_password: str, new_password: str
    ) -> None:
        if not user.hashed_password or not verify_password(old_password, user.hashed_password):
            raise ForbiddenError()
        user.hashed_password = hash_password(new_password)

        # Revoke all existing refresh tokens for security
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id
        ).update({"revoked": True})

        db.commit()
        logger.info("Password changed for user: %s", user.id)

    def get_or_create_oauth_user(
        self,
        db: Session,
        provider: str,
        provider_user_id: str,
        email: str,
        name: Optional[str],
        avatar_url: Optional[str] = None,
    ) -> User:
        """
        Find or create a user from OAuth callback.
        Never creates duplicate users for same email.
        """
        # Check if we already have an OAuth account for this provider+id
        oauth_account = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
            .first()
        )

        if oauth_account:
            if name:
                oauth_account.user.name = name
            if avatar_url:
                oauth_account.user.avatar_url = avatar_url
            db.commit()
            return oauth_account.user

        normalized_email = email.lower().strip()
        existing_user = db.query(User).filter(User.email == normalized_email).first()
        if existing_user:
            raise ConflictError(
                "An account with this email already exists. Sign in to that account before linking another provider."
            )

        user = User(
            id=str(uuid.uuid4()),
            email=normalized_email,
            name=name,
            avatar_url=avatar_url,
            is_active=True,
            is_verified=True,
        )
        db.add(user)
        db.flush()

        profile = Profile(id=str(uuid.uuid4()), user_id=user.id)
        db.add(profile)
        db.flush()

        # Create OAuth account record
        new_oauth = OAuthAccount(
            id=str(uuid.uuid4()),
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=email,
        )
        db.add(new_oauth)
        db.commit()
        db.refresh(user)

        logger.info("OAuth user %s via %s: %s", "created/linked", provider, user.id)
        return user

    def link_oauth_identity(
        self,
        db: Session,
        user: User,
        provider: str,
        provider_user_id: str,
        email: str,
        avatar_url: Optional[str] = None,
    ) -> None:
        """Link an identity only after an authenticated user explicitly starts OAuth linking."""
        identity = (
            db.query(OAuthAccount)
            .filter(
                OAuthAccount.provider == provider,
                OAuthAccount.provider_user_id == provider_user_id,
            )
            .first()
        )
        if identity:
            if identity.user_id != user.id:
                raise ConflictError("This provider account is already linked to another Aarogya account")
            return

        identity = OAuthAccount(
            id=str(uuid.uuid4()),
            user_id=user.id,
            provider=provider,
            provider_user_id=provider_user_id,
            provider_email=email,
        )
        db.add(identity)
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        db.commit()

    def _issue_refresh_token(
        self, db: Session, user_id: str, family: Optional[str] = None
    ) -> tuple[str, RefreshToken]:
        """Generate and store a hashed refresh token."""
        import uuid
        raw = generate_refresh_token()
        token_hash = hash_refresh_token(raw)
        family = family or generate_token_family()

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        record = RefreshToken(
            id=str(uuid.uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            family=family,
        )
        db.add(record)
        return raw, record


from app.models.profile import Profile  # noqa: E402

auth_service = AuthService()
