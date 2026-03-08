from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from loguru import logger


PUBLIC_ROUTES = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/send-otp",
    "/api/v1/auth/verify-otp",
    "/api/v1/auth/refresh-token",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Lightweight auth middleware.

    Purpose:
    - Quickly reject requests that lack Authorization headers.
    - Avoid unnecessary JWT decoding and DB calls.

    Note:
    Actual authentication (token verification & user loading)
    is handled later by dependencies like `get_current_user`.
    """

    def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path

        # Allow CORS preflight
        if request.method == "OPTIONS":
            return call_next(request)

        # Allow public routes
        if self.is_public_route(path):
            return call_next(request)

        # Validate Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            logger.warning(f"Authorization header missing | path={path}")
            return self._unauthorized("Authorization header missing")

        if not auth_header.startswith("Bearer "):
            logger.warning(f"Invalid Authorization format | path={path}")
            return self._unauthorized(
                "Invalid Authorization format. Use: Bearer <token>"
            )

        return call_next(request)

    @staticmethod
    def is_public_route(path: str) -> bool:
        return any(path.startswith(route) for route in PUBLIC_ROUTES)

    @staticmethod
    def _unauthorized(message: str) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={
                "success": False,
                "detail": message,
            },
        )