import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.routes import api_router
from app.config import settings
from app.db import Base, engine
import app.models  # noqa: F401

# Automatically initialize database schema
try:
    Base.metadata.create_all(bind=engine)
except Exception as exc:
    print(f"Database schema auto-creation notice: {exc}")

app = FastAPI(
    title="DealDNA AI — The Revenue Memory Engine",
    version="1.1.0",
    description="Persistent memory-powered revenue intelligence agent for deal tracking, context, and recommendations.",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow frontend origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID"],
)


@app.middleware("http")
async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or f"corr-{uuid.uuid4().hex[:12]}"
    request.state.correlation_id = correlation_id
    response = await call_next(request)
    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = getattr(request.state, "correlation_id", "unknown")
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "message": str(exc),
            "correlation_id": correlation_id,
            "details": {},
        },
    )


app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "dealdna-api",
        "version": "1.1.0",
        "environment": settings.app_env,
    }


@app.get("/")
def root():
    return {
        "message": "Welcome to DealDNA AI — The Revenue Memory Engine API",
        "version": "1.1.0",
        "docs_url": "/docs",
    }
