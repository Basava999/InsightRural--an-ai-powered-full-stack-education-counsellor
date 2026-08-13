"""Admin panel endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Header

from app.config import get_settings
from app.core.security import decode_token, require_role

router = APIRouter()
settings = get_settings()


def verify_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Admin authentication required")
    token = authorization.split(" ", 1)[1]
    payload = decode_token(token)
    if not payload or not require_role(payload.get("role", ""), ("admin",)):
        raise HTTPException(403, "Admin role required")
    return payload


@router.get("/status")
async def admin_status(_=Depends(verify_admin)):
    return {
        "platform": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "engine_version": settings.ENGINE_VERSION,
        "data_mode": "json" if settings.USE_JSON_DATA else "postgresql",
    }


@router.post("/ml/retrain")
async def retrain_models(_=Depends(verify_admin)):
    from app.ml.train import train_and_evaluate
    result = train_and_evaluate(settings.DATA_DIR, settings.ML_MODELS_DIR)
    return result
