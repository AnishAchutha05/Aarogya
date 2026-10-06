"""Progress photo service with storage abstraction."""

import logging
import mimetypes
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.errors import ForbiddenError, NotFoundError
from app.models.photo import ProgressPhoto

logger = logging.getLogger(__name__)

ALLOWED_MIME_TYPES = set(settings.ALLOWED_IMAGE_TYPES)
MAX_SIZE_BYTES = settings.MAX_PHOTO_SIZE_MB * 1024 * 1024


class PhotoStorageBackend:
    """
    Abstract storage interface.
    Swap implementation for S3/GCS without changing PhotoService.
    """

    def save(self, data: bytes, key: str, mime_type: str) -> str:
        raise NotImplementedError

    def delete(self, key: str) -> None:
        raise NotImplementedError

    def get_serving_path(self, key: str) -> str:
        raise NotImplementedError


class LocalPhotoStorage(PhotoStorageBackend):
    """Local filesystem storage for photos."""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save(self, data: bytes, key: str, mime_type: str) -> str:
        path = self.base_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return key

    def delete(self, key: str) -> None:
        path = self.base_dir / key
        if path.exists():
            path.unlink()

    def get_serving_path(self, key: str) -> str:
        return str(self.base_dir / key)


# Default storage backend - can be swapped via DI later
def get_storage_backend() -> PhotoStorageBackend:
    return LocalPhotoStorage(settings.UPLOAD_DIR)


class PhotoService:

    def __init__(self, storage: Optional[PhotoStorageBackend] = None):
        self.storage = storage or get_storage_backend()

    async def upload_photo(
        self,
        db: Session,
        user_id: str,
        file: UploadFile,
        photo_date=None,
        notes: Optional[str] = None,
    ) -> ProgressPhoto:
        # Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            from app.core.errors import AarogyaError
            from fastapi import status
            raise AarogyaError(
                f"File type not allowed. Allowed: {', '.join(ALLOWED_MIME_TYPES)}",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Read and validate size
        data = await file.read()
        if len(data) > MAX_SIZE_BYTES:
            from app.core.errors import AarogyaError
            from fastapi import status
            raise AarogyaError(
                f"File too large. Maximum {settings.MAX_PHOTO_SIZE_MB}MB.",
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        # Validate that it's actually an image (basic header check)
        self._validate_image_bytes(data, file.content_type)

        # Generate a safe storage key - never use user-provided filename as path
        extension = mimetypes.guess_extension(file.content_type) or ".jpg"
        storage_key = f"{user_id}/{uuid.uuid4()}{extension}"

        # Sanitize original filename for display
        original = Path(file.filename or "").name if file.filename else None
        if original:
            original = "".join(c for c in original if c.isalnum() or c in "._- ")[:255]

        self.storage.save(data, storage_key, file.content_type)

        photo = ProgressPhoto(
            id=str(uuid.uuid4()),
            user_id=user_id,
            storage_key=storage_key,
            original_filename=original,
            mime_type=file.content_type,
            file_size_bytes=len(data),
            photo_date=photo_date,
            notes=notes,
        )
        db.add(photo)
        db.commit()
        db.refresh(photo)
        logger.info("Photo uploaded user=%s photo=%s", user_id, photo.id)
        return photo

    def list_photos(self, db: Session, user_id: str) -> list[ProgressPhoto]:
        return (
            db.query(ProgressPhoto)
            .filter(ProgressPhoto.user_id == user_id)
            .order_by(ProgressPhoto.created_at.desc())
            .all()
        )

    def get_photo(
        self, db: Session, photo_id: str, user_id: str
    ) -> ProgressPhoto:
        photo = db.get(ProgressPhoto, photo_id)
        if not photo:
            raise NotFoundError("Photo")
        if photo.user_id != user_id:
            raise ForbiddenError()
        return photo

    def delete_photo(
        self, db: Session, photo_id: str, user_id: str
    ) -> None:
        photo = self.get_photo(db, photo_id, user_id)
        try:
            self.storage.delete(photo.storage_key)
        except Exception as e:
            logger.warning("Failed to delete file storage_key=%s: %s", photo.storage_key, e)
        db.delete(photo)
        db.commit()

    def get_file_path(self, db: Session, photo_id: str, user_id: str) -> str:
        photo = self.get_photo(db, photo_id, user_id)
        return self.storage.get_serving_path(photo.storage_key)

    @staticmethod
    def _validate_image_bytes(data: bytes, mime_type: str) -> None:
        """Basic magic-byte validation to prevent file type spoofing."""
        MAGIC = {
            "image/jpeg": [b"\xff\xd8\xff"],
            "image/png": [b"\x89PNG"],
            "image/gif": [b"GIF87a", b"GIF89a"],
            "image/webp": [b"RIFF"],
        }
        signatures = MAGIC.get(mime_type, [])
        if signatures and not any(data.startswith(sig) for sig in signatures):
            from app.core.errors import AarogyaError
            from fastapi import status
            raise AarogyaError(
                "File content does not match declared type",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )


photo_service = PhotoService()
