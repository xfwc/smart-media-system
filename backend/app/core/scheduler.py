"""Cron scheduler — hourly Douyin hot list crawl."""
import json
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from app.db.session import _get_engine
from app.db.redis import get_redis
from app.models.hot_models import HotRanking
from sqlalchemy import select

CACHE_KEY = "hot:rankings:latest"
CACHE_TTL = 300
scheduler = AsyncIOScheduler()


async def _crawl_job():
    """Hourly: crawl -> save -> update cache."""
    from app.services.crawler.hot_service import crawl_and_save

    _, sessionmaker = _get_engine()
    async with sessionmaker() as session:
        try:
            saved = await crawl_and_save(session)
            if saved > 0:
                redis = await get_redis()
                if redis:
                    result = await session.execute(
                        select(HotRanking).order_by(
                            HotRanking.crawled_at.desc(), HotRanking.rank.asc()).limit(50)
                    )
                    items = result.scalars().all()
                    data = [
                        {"rank": r.rank, "title": r.title, "hot_value": r.hot_value,
                         "url": r.url, "label": r.label,
                         "crawled_at": r.crawled_at.isoformat() if r.crawled_at else None}
                        for r in items
                    ]
                    await redis.setex(CACHE_KEY, CACHE_TTL, json.dumps(data, ensure_ascii=False))
        except Exception as e:
            logger.error(f"Crawl job error: {e}")


def start_scheduler():
    scheduler.add_job(_crawl_job, "interval", hours=1, id="crawl_hourly", replace_existing=True)
    scheduler.add_job(_crawl_job, id="crawl_startup", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler: crawl hourly + on startup")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
