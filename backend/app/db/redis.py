from redis.asyncio import Redis, ConnectionPool
from app.core.config import settings

redis_pool = ConnectionPool.from_url(settings.REDIS_URL, max_connections=50)


async def get_redis() -> Redis:
    return Redis(connection_pool=redis_pool)


# Global Redis instance for simple access
redis_client: Redis | None = None


async def init_redis():
    global redis_client
    redis_client = await get_redis()


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
