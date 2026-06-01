from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from app.core.config import settings

engine = create_async_engine(settings.MYSQL_URL, echo=settings.DEBUG, pool_size=20, max_overflow=10)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
