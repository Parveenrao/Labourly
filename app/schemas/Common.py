from pydantic import BaseModel, field_validator
from typing import Generic, TypeVar, Optional, List, Any
from datetime import datetime

T = TypeVar("T")


# ─── Standard API Response ───────────────────────────────────────
class APIResponse(BaseModel, Generic[T]):
    """
    Standard wrapper for all API responses.
    Usage: APIResponse(data=worker, message="Profile created")
    """
    success: bool = True
    message: str = "OK"
    data: Optional[T] = None


# ─── Error Response ──────────────────────────────────────────────
class ErrorResponse(BaseModel):
    """
    Standard error response shape.
    Returned by global exception handlers in main.py
    """
    success: bool = False
    detail: str
    errors: Optional[List[dict]] = None     # validation errors list


# ─── Empty Success Response ──────────────────────────────────────
class SuccessResponse(BaseModel):
    """For actions that don't return data e.g. mark as read, delete"""
    success: bool = True
    message: str = "OK"


# ─── Paginated Response ──────────────────────────────────────────
class PaginatedResponse(BaseModel, Generic[T]):
    """
    Paginated list response with metadata.
    Usage: PaginatedResponse(data=workers, page=1, page_size=20, total=100, total_pages=5)
    """
    success: bool = True
    data: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int

    @property
    def has_next(self) -> bool:
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


# ─── Pagination Query Params ─────────────────────────────────────
class PaginationParams(BaseModel):
    """Reusable pagination query params for routes"""
    page: int = 1
    page_size: int = 20

    @field_validator("page")
    def validate_page(cls, v):
        if v < 1:
            raise ValueError("Page must be at least 1")
        return v

    @field_validator("page_size")
    def validate_page_size(cls, v):
        if v < 1 or v > 100:
            raise ValueError("Page size must be between 1 and 100")
        return v


# ─── Health Check Response ───────────────────────────────────────
class HealthResponse(BaseModel):
    status: str = "ok"
    app: str
    version: str = "1.0.0"
