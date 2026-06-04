"""APScheduler integration — runs crawl on startup and every hour."""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.services.crawler.douyin_crawler import run_crawl
from app.db.session import _get_engine
from sqlalchemy.ext.asyncio import AsyncSession

scheduler = AsyncIOScheduler()


async def _crawl_job():
    """Wrap crawl with session management."""
    _, sessionmaker = _get_engine()
    async with sessionmaker() as session:
        try:
            await run_crawl(session)
        except Exception as e:
            print(f"[Crawler] Error: {e}")


def start_scheduler():
    scheduler.add_job(_crawl_job, "interval", hours=1, id="crawl_hourly", replace_existing=True)
    # Also run immediately on startup
    scheduler.add_job(_crawl_job, id="crawl_startup", replace_existing=True)
    scheduler.start()
    print("[Scheduler] Started — crawls every hour + on startup")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
