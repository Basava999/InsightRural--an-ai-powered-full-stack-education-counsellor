"""Security utilities — JWT, input validation, RBAC."""

import hashlib
import hmac
import time
from typing import Optional

from app.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    return hmac.compare_digest(hash_password(password), hashed)


def create_access_token(user_id: str, role: str = "student") -> str:
    import jwt
    payload = {
        "sub": user_id,
        "role": role,
        "exp": time.time() + settings.JWT_EXPIRE_MINUTES * 60,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    import jwt
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None


def require_role(user_role: str, allowed: tuple) -> bool:
    return user_role in allowed
