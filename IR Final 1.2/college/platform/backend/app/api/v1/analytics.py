"""Analytics dashboard endpoints."""

from fastapi import APIRouter

from app.config import get_settings
from app.services.data_service import get_data_service

router = APIRouter()
settings = get_settings()


@router.get("/overview")
async def analytics_overview():
    svc = get_data_service()
    colleges = svc.get_all_colleges()
    types = {}
    cities = {}
    for c in colleges:
        t = c.get("type", "Unknown")
        types[t] = types.get(t, 0) + 1
        loc = (c.get("location") or "Unknown").split(",")[0]
        cities[loc] = cities.get(loc, 0) + 1
    return {
        "total_colleges": len(colleges),
        "by_type": types,
        "top_cities": dict(sorted(cities.items(), key=lambda x: x[1], reverse=True)[:10]),
        "total_scholarships": len(svc.scholarships),
        "total_hostels": len(svc.hostels),
        "engine_version": settings.ENGINE_VERSION,
    }
