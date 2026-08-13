# ==============================================================================
# InsightRural — Authentication Router
# ==============================================================================
# Endpoints: /auth/signup, /auth/login, /auth/me, /profile
# Migrated from app.py Flask endpoints (lines 244-1144)
# ==============================================================================

import json
import hmac
import hashlib
import base64
import time
from functools import wraps
from typing import Dict, Any, Optional

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from core.logging import get_logger
from core.config import settings

logger = get_logger("api.auth")
router = APIRouter()


# ── JWT Utilities (Custom HMAC-SHA256, preserves app.py implementation) ───────

def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (4 - (len(data) % 4))
    return base64.urlsafe_b64decode(data + padding)


def generate_token(user_id: int, expires_in: int = None) -> str:
    """Generate a custom JWT token signed with HMAC-SHA256."""
    if expires_in is None:
        expires_in = settings.JWT_EXPIRY_SECONDS

    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"user_id": user_id, "exp": int(time.time()) + expires_in}
    header_b64 = _b64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(
        settings.JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
    ).digest()
    signature_b64 = _b64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{signature_b64}"


def decode_token(token: str) -> Optional[int]:
    """Decode and verify custom JWT token. Returns user_id if valid, else None."""
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, signature_b64 = parts
        signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
        expected_sig = hmac.new(
            settings.JWT_SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        expected_sig_b64 = _b64url_encode(expected_sig)
        if not hmac.compare_digest(
            signature_b64.encode("utf-8"), expected_sig_b64.encode("utf-8")
        ):
            return None
        payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        if payload.get("exp", 0) < time.time():
            return None
        return payload.get("user_id")
    except Exception:
        return None


async def get_current_user_id(request: Request) -> int:
    """FastAPI dependency to extract and validate JWT token."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication token is missing")
    token = auth_header.split(" ", 1)[1]
    user_id = decode_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user_id


# ── Request Models ────────────────────────────────────────────────────────────

class AuthRequest(BaseModel):
    email: str
    password: str
    profile: Optional[Dict[str, Any]] = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/auth/signup")
async def auth_signup(data: AuthRequest):
    """Register a new user account."""
    from db import SessionLocal
    from db_models import User
    from werkzeug.security import generate_password_hash

    email = data.email.strip().lower()
    if not email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    session = SessionLocal()
    try:
        existing = session.query(User).filter(User.email == email).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="An account with this email already exists"
            )

        password_hash = generate_password_hash(data.password)
        new_user = User(
            email=email, password_hash=password_hash, profile=data.profile or {}
        )
        session.add(new_user)
        session.commit()

        token = generate_token(new_user.id)
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "token": token,
                "user": {
                    "id": new_user.id,
                    "email": new_user.email,
                    "profile": new_user.profile or {},
                },
            },
        )
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        logger.error("Signup error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    finally:
        session.close()


@router.post("/auth/login")
async def auth_login(data: AuthRequest):
    """Authenticate user and return JWT token."""
    from db import SessionLocal
    from db_models import User
    from werkzeug.security import check_password_hash

    email = data.email.strip().lower()
    if not email or not data.password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.email == email).first()
        if not user or not check_password_hash(user.password_hash, data.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = generate_token(user.id)
        return {
            "success": True,
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "profile": user.profile or {},
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Login error: %s", e, exc_info=True)
        return JSONResponse(
            status_code=500, content={"success": False, "error": str(e)}
        )
    finally:
        session.close()


@router.get("/auth/me")
async def auth_me(user_id: int = Depends(get_current_user_id)):
    """Get current authenticated user profile."""
    from db import SessionLocal
    from db_models import User

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "success": True,
            "user": {
                "id": user.id,
                "email": user.email,
                "profile": user.profile or {},
            },
        }
    finally:
        session.close()


@router.api_route("/profile", methods=["GET", "POST"])
async def manage_profile(request: Request, user_id: int = Depends(get_current_user_id)):
    """Store or retrieve student profile in database."""
    from db import SessionLocal
    from db_models import User

    session = SessionLocal()
    try:
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if request.method == "POST":
            profile = await request.json()
            user.profile = profile
            session.commit()
            return {"status": "saved", "profile": profile}
        else:
            return user.profile or {}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        session.close()
