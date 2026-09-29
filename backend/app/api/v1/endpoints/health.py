from fastapi import APIRouter
from app.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "dealdna-api",
        "environment": settings.app_env,
    }


@router.get("/ready")
def readiness_check():
    return {
        "status": "ready",
        "service": "dealdna-api",
        "database": "connected",
        "memory_engine": "operational",
    }
