from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from loguru import logger

from app.core.config import settings
from app.core.Logging import setup_logging
from app.middleware.logging_middleware import LoggingMiddleware

from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.core.database import check_db_connection
from app.core.redis import check_redis_connection
from app.core.database import create_all_tables


# --------------------------------------
# Setup Logging
# --------------------------------------
setup_logging()


# ---------------------------------------
# Create FastAPI App
# ---------------------------------------

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Worker-first job platform for informal laborers in India",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)


# -----------------------------------------
# Middleware
# ──------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)


# ─--------------------------------------
# Exception Handlers
# -----------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {"field": e["loc"][-1], "message": e["msg"]}
        for e in exc.errors()
    ]

    logger.warning(f"Validation error | path={request.url.path} | errors={errors}")

    return JSONResponse(
        status_code=422,
        content={"success": False, "errors": errors},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error | path={request.url.path} | error={str(exc)}")

    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Internal server error"},
    )


# ----------------------------------------------
# Routers
# -------------------------------------------
from app.api.v1 import (
    auth,
    user,
    worker,
    employer,
    jobs,
    rating,
    notifications,
)

API_PREFIX = settings.API_V1_PREFIX

app.include_router(auth.router, prefix=f"{API_PREFIX}/auth", tags=["Auth"])
app.include_router(user.router, prefix=f"{API_PREFIX}/users", tags=["Users"])
app.include_router(worker.router, prefix=f"{API_PREFIX}/workers", tags=["Workers"])
app.include_router(employer.router, prefix=f"{API_PREFIX}/employers", tags=["Employers"])
app.include_router(jobs.router, prefix=f"{API_PREFIX}/jobs", tags=["Jobs"])
app.include_router(rating.router, prefix=f"{API_PREFIX}/ratings", tags=["Ratings"])
app.include_router(notifications.router, prefix=f"{API_PREFIX}/notifications", tags=["Notifications"])


# ------------------------------------------
# Startup / Shutdown
# ------------------------------------------
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}...")

    import app.models

    check_db_connection()
    check_redis_connection()
    create_all_tables()

    logger.info("Database tables created")
    logger.info("Startup complete")

    yield

# ---------------------------------------
# Health Check
# ---------------------------------------
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }