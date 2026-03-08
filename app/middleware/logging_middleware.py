import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from loguru import logger


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next) -> Response:
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id

        method = request.method
        path = request.url.path
        client_ip = request.client.host if request.client else "unknown"

        start_time = time.perf_counter()

        logger.info(f"{request_id} {method} {path} started ip={client_ip}")

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = (time.perf_counter() - start_time) * 1000
            logger.exception(
                f"{request_id} {method} {path} error duration={duration:.2f}ms message={exc}"
            )
            raise

        duration = (time.perf_counter() - start_time) * 1000
        status = response.status_code

        if status < 300:
            logger.info(
                f"{request_id} {method} {path} status={status} duration={duration:.2f}ms"
            )
        elif status < 500:
            logger.warning(
                f"{request_id} {method} {path} status={status} duration={duration:.2f}ms"
            )
        else:
            logger.error(
                f"{request_id} {method} {path} status={status} duration={duration:.2f}ms"
            )

        response.headers["X-Request-ID"] = request_id
        return response