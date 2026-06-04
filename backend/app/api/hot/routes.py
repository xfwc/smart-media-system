import json
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.db.session import get_db
from app.db.redis import get_redis
from app.models.hot import HotTopic, TopicAnalysis
from app.models.hot_models import HotRanking
from app.schemas.hot import HotTopicItem, HotTopicListResponse, HotTopicDetail, TopicAnalysisResponse
from app.schemas.common import ApiResponse

router = APIRouter()
CACHE_KEY = "hot:rankings:latest"
CACHE_TTL = 300
VALID_CATEGORIES = ["时政", "财经", "科技", "娱乐", "体育", "美食", "教育", "其他"]


# ─── New: Douyin hot ranking APIs ───

@router.get("/hot/latest")
async def get_latest(session: AsyncSession = Depends(get_db)):
    """Get latest hot rankings from Redis cache or DB."""
    redis = await get_redis()
    if redis:
        cached = await redis.get(CACHE_KEY)
        if cached:
            return json.loads(cached)

    result = await session.execute(
        select(HotRanking).order_by(HotRanking.crawled_at.desc(), HotRanking.rank.asc()).limit(50)
    )
    items = [
        {"rank": r.rank, "title": r.title, "hot_value": r.hot_value,
         "url": r.url, "label": r.label,
         "video_count": r.video_count, "view_count": r.view_count,
         "crawled_at": r.crawled_at.isoformat() if r.crawled_at else None}
        for r in result.scalars().all()
    ]
    if redis and items:
        await redis.setex(CACHE_KEY, CACHE_TTL, json.dumps(items, ensure_ascii=False))
    return {"total": len(items), "items": items, "updated_at": datetime.utcnow().isoformat()}


@router.get("/hot/history")
async def get_history(
    target_date: str = Query(None, alias="date"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    session: AsyncSession = Depends(get_db),
):
    """Get hot rankings for a specific date."""
    if target_date:
        try:
            dt = datetime.strptime(target_date, "%Y-%m-%d")
        except ValueError:
            return {"detail": "日期格式: YYYY-MM-DD"}, 400
        start = dt.replace(hour=0, minute=0, second=0)
        end = dt.replace(hour=23, minute=59, second=59)
        query = select(HotRanking).where(HotRanking.crawled_at.between(start, end))
    else:
        query = select(HotRanking)

    query = query.order_by(HotRanking.crawled_at.desc(), HotRanking.rank.asc())
    total = len((await session.execute(query)).scalars().all())
    result = await session.execute(query.offset((page - 1) * page_size).limit(page_size))

    return {
        "total": total, "page": page, "page_size": page_size,
        "items": [
            {"rank": r.rank, "title": r.title, "hot_value": r.hot_value,
             "label": r.label, "crawled_at": r.crawled_at.isoformat() if r.crawled_at else None}
            for r in result.scalars().all()
        ],
    }


@router.post("/hot/crawl")
async def trigger_crawl(session: AsyncSession = Depends(get_db)):
    """Manual crawl trigger."""
    from app.services.crawler.hot_service import crawl_and_save
    saved = await crawl_and_save(session)
    return ApiResponse(message=f"Crawl done: {saved} new items")


# ─── Legacy: Hot topic list/detail (from hot_topics table) ───

@router.get("/hot/list")
async def get_hot_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    category: str | None = Query(None),
    keyword: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    query = select(HotTopic).order_by(HotTopic.heat_value.desc())
    if category and category in VALID_CATEGORIES:
        query = query.where(HotTopic.category == category)
    if keyword:
        query = query.where(HotTopic.title.contains(keyword))

    result = await session.execute(query)
    all_topics = list(result.scalars().all())

    # Fallback to hot_rankings
    if not all_topics:
        rank_result = await session.execute(
            select(HotRanking).order_by(HotRanking.crawled_at.desc(), HotRanking.rank.asc()).limit(50)
        )
        rankings = list(rank_result.scalars().all())
        items = [
            HotTopicItem(id=r.id, title=r.title, rank=r.rank, heat_value=r.hot_value,
                         category=r.label, source="抖音热榜",
                         collected_at=r.crawled_at.isoformat() if r.crawled_at else None)
            for r in rankings
        ]
        return HotTopicListResponse(total=len(items), page=1, page_size=50, items=items,
                                     updated_at=rankings[0].crawled_at.isoformat() if rankings else None)

    for i, t in enumerate(all_topics):
        t.display_rank = i + 1
    total = len(all_topics)
    paged = all_topics[(page - 1) * page_size: page * page_size]
    items = [
        HotTopicItem(id=t.id, title=t.title, rank=t.display_rank, heat_value=t.heat_value,
                     category=t.category, source=t.source,
                     collected_at=t.collected_at.isoformat() if t.collected_at else None)
        for t in paged
    ]
    return HotTopicListResponse(
        total=total, page=page, page_size=page_size, items=items,
        updated_at=all_topics[0].collected_at.isoformat() if all_topics else None,
    )


@router.get("/hot/{topic_id}")
async def get_hot_detail(topic_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(
        select(HotTopic).options(selectinload(HotTopic.analysis)).where(HotTopic.id == topic_id)
    )
    topic = result.scalar_one_or_none()
    if not topic:
        return {"detail": "Not found"}, 404
    risk_level = topic.analysis.risk_level.value if topic.analysis and topic.analysis.risk_level else None
    return HotTopicDetail(
        id=topic.id, title=topic.title, rank=topic.rank, heat_value=topic.heat_value,
        category=topic.category, source=topic.source, summary=topic.summary,
        detail_text=topic.detail_text, risk_level=risk_level,
        collected_at=topic.collected_at.isoformat() if topic.collected_at else None,
    )


@router.get("/hot/{topic_id}/analysis")
async def get_analysis(topic_id: int, session: AsyncSession = Depends(get_db)):
    result = await session.execute(select(TopicAnalysis).where(TopicAnalysis.topic_id == topic_id))
    analysis = result.scalar_one_or_none()
    if not analysis:
        return {"detail": "Not found"}, 404
    return TopicAnalysisResponse(
        topic_id=analysis.topic_id,
        keywords=analysis.keywords if isinstance(analysis.keywords, list) else [],
        category=analysis.category,
        sentiment=analysis.sentiment.value if analysis.sentiment else "neutral",
        sentiment_score=analysis.sentiment_score,
        risk_level=analysis.risk_level.value if analysis.risk_level else "low",
        risk_reason=analysis.risk_reason,
        analyzed_at=analysis.analyzed_at.isoformat() if analysis.analyzed_at else None,
    )
