import traceback
from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings

redis_pool = None
redis_client: Redis | None = None


async def get_redis() -> Redis | None:
    """Get Redis client if available, returns None if Redis is down."""
    global redis_client
    if redis_client is not None:
        return redis_client
    try:
        redis_client = Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2)
        await redis_client.ping()
        return redis_client
    except Exception:
        return None


async def init_redis():
    try:
        global redis_pool, redis_client
        redis_pool = ConnectionPool.from_url(
            settings.REDIS_URL, max_connections=20, socket_connect_timeout=2,
        )
        redis_client = Redis(connection_pool=redis_pool)
        await redis_client.ping()
        print("[Redis] Connected")
    except Exception:
        print("[Redis] Unavailable — running without cache")
        redis_client = None


async def close_redis():
    global redis_client, redis_pool
    if redis_client:
        try:
            await redis_client.close()
        except Exception:
            pass
        redis_client = None
    redis_pool = None
