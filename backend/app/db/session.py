import os
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy import create_engine as create_sync_engine
from app.core.config import settings

_engine = None
_AsyncSessionLocal = None


def _get_engine():
    """Smart engine selection: MySQL if available, SQLite as local fallback."""
    global _engine, _AsyncSessionLocal
    if _engine is not None:
        return _engine, _AsyncSessionLocal

    # Use SQLite for local dev if no MYSQL_URL override set
    use_sqlite = os.environ.get("USE_SQLITE", "").lower() in ("1", "true", "yes")
    mysql_url = settings.MYSQL_URL  # Default always points to MySQL

    if use_sqlite or (
        "localhost" in mysql_url
        and not os.environ.get("MYSQL_URL")
        and not os.environ.get("DOCKER_ENV")
    ):
        # Local development without Docker — use SQLite
        print("[DB] Local dev mode: using SQLite")
        _engine = create_async_engine("sqlite+aiosqlite:///./smart_media.db", echo=False)

        # Auto-create tables for SQLite
        sync_engine = create_sync_engine("sqlite:///./smart_media.db", echo=False)
        from app.models import Base
        Base.metadata.create_all(sync_engine)
    else:
        print(f"[DB] Using MySQL at {mysql_url.split('@')[1] if '@' in mysql_url else mysql_url}")
        _engine = create_async_engine(
            mysql_url, echo=settings.DEBUG,
            pool_size=10, max_overflow=5, pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "asyncmy" in mysql_url else {},
        )

    _AsyncSessionLocal = async_sessionmaker(
        _engine, class_=AsyncSession, expire_on_commit=False,
    )
    return _engine, _AsyncSessionLocal


async def get_db() -> AsyncSession:
    _, sessionmaker = _get_engine()
    async with sessionmaker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
