"""API v1 routers."""

from fastapi import APIRouter

from app.api.v1 import predict, colleges, chat, hostels, scholarships, analytics, admin

router = APIRouter()
router.include_router(predict.router, prefix="/predict", tags=["College Predictor"])
router.include_router(colleges.router, prefix="/colleges", tags=["College Explorer"])
router.include_router(chat.router, prefix="/chat", tags=["Counselling Chatbot"])
router.include_router(hostels.router, prefix="/hostels", tags=["Hostels"])
router.include_router(scholarships.router, prefix="/scholarships", tags=["Scholarships"])
router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
router.include_router(admin.router, prefix="/admin", tags=["Admin"])
