from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Fixed-window rate limit per client IP, backed by Redis INCR/EXPIRE.

    Reads its Redis client from `request.app.state.get_redis` (set at app startup)
    rather than importing one directly, so tests can swap in a fake Redis instance.
    """

    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        redis_client = request.app.state.get_redis()
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{client_ip}"

        count = redis_client.incr(key)
        if count == 1:
            redis_client.expire(key, 60)

        if count > settings.rate_limit_per_minute:
            return JSONResponse(status_code=429, content={"detail": "Rate limit exceeded"})

        return await call_next(request)
