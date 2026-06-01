from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

mongo_client: AsyncIOMotorClient | None = None
mongo_db: AsyncIOMotorDatabase | None = None


async def init_mongodb():
    global mongo_client, mongo_db
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    mongo_db = mongo_client.smart_media

    # Ensure collections exist
    collections = await mongo_db.list_collection_names()
    for col_name in [
        settings.MONGO_CRAWL_COLLECTION,
        settings.MONGO_API_LOGS_COLLECTION,
        settings.MONGO_AI_LOGS_COLLECTION,
        settings.MONGO_ARCHIVE_COLLECTION,
    ]:
        if col_name not in collections:
            await mongo_db.create_collection(col_name)


async def close_mongodb():
    global mongo_client
    if mongo_client:
        mongo_client.close()
        mongo_client = None


def get_mongo_db() -> AsyncIOMotorDatabase:
    if mongo_db is None:
        raise RuntimeError("MongoDB not initialized. Call init_mongodb() first.")
    return mongo_db
