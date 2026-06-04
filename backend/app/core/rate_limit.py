import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException
from app.core.config import settings
from app.db.redis import get_redis


class TokenBucketLimiter:
    """Token bucket rate limiter using Redis."""

    def __init__(self):
        self.max_tokens = settings.RATE_LIMIT_REQUESTS
        self.refill_rate = settings.RATE_LIMIT_REQUESTS / settings.RATE_LIMIT_WINDOW_SECONDS
        self.window = settings.RATE_LIMIT_WINDOW_SECONDS

    async def is_allowed(self, key: str) -> bool:
        redis = await get_redis()
        bucket_key = f"rate_limit:{key}"

        pipe = redis.pipeline()
        current = await redis.hgetall(bucket_key)
        now = time.time()

        if not current:
            await redis.hset(bucket_key, mapping={"tokens": self.max_tokens - 1, "last_refill": now})
            await redis.expire(bucket_key, self.window + 10)
            return True

        tokens = float(current.get("tokens", self.max_tokens))
        last_refill = float(current.get("last_refill", now))
        elapsed = now - last_refill
        new_tokens = min(self.max_tokens, tokens + elapsed * self.refill_rate)

        if new_tokens >= 1:
            await redis.hset(bucket_key, mapping={"tokens": new_tokens - 1, "last_refill": now})
            return True
        return False


limiter = TokenBucketLimiter()


async def rate_limit_dependency(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    allowed = await limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
