import hashlib
import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.config import settings
from app.database import get_redis

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Redis sliding-window rate limit for inference routes (/v1/*)."""

    async def dispatch(self, request: Request, call_next):
        if not request.url.path.startswith("/v1/"):
            return await call_next(request)

        identifier = self._client_identifier(request)
        redis_key = f"rate_limit:{identifier}"

        try:
            redis = get_redis()
            count = await redis.incr(redis_key)
            if count == 1:
                await redis.expire(redis_key, settings.RATE_LIMIT_WINDOW_SECONDS)
            if count > settings.RATE_LIMIT_REQUESTS:
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "rate_limit_exceeded",
                        "detail": "Too many requests. Please try again later.",
                    },
                    headers={
                        "Retry-After": str(settings.RATE_LIMIT_WINDOW_SECONDS),
                    },
                )
        except RuntimeError:
            logger.warning("Redis unavailable; rate limiting skipped")
        except Exception:
            logger.exception("Rate limit check failed; allowing request")

        return await call_next(request)

    @staticmethod
    def _client_identifier(request: Request) -> str:
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return "key:" + hashlib.sha256(api_key.encode()).hexdigest()[:32]
        host = request.client.host if request.client else "unknown"
        return f"ip:{host}"
