from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

mongo_client: AsyncIOMotorClient | None = None
mongo_db: AsyncIOMotorDatabase | None = None


async def init_mongodb():
    global mongo_client, mongo_db
    try:
        mongo_client = AsyncIOMotorClient(
            settings.MONGODB_URL, serverSelectionTimeoutMS=2000,
        )
        mongo_db = mongo_client.smart_media
        await mongo_client.admin.command("ping")
        print("[MongoDB] Connected")
    except Exception:
        print("[MongoDB] Unavailable — running without document logging")
        mongo_client = None
        mongo_db = None


async def close_mongodb():
    global mongo_client
    if mongo_client:
        try:
            mongo_client.close()
        except Exception:
            pass
        mongo_client = None


def get_mongo_db() -> AsyncIOMotorDatabase | None:
    return mongo_db
