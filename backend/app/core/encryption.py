import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet() -> Fernet:
    key = hashlib.sha256(
        settings.AI_KEY_ENCRYPTION_KEY.encode()
    ).digest()

    encoded = base64.urlsafe_b64encode(key)

    return Fernet(encoded)


def encrypt_api_key(value: str) -> str:
    return _fernet().encrypt(value.encode()).decode()


def decrypt_api_key(value: str) -> str:
    return _fernet().decrypt(value.encode()).decode()
