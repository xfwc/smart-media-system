from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.hot import HotTopic, TopicAnalysis
from app.schemas.hot import HotTopicItem, HotTopicListResponse, HotTopicDetail, TopicAnalysisResponse

router = APIRouter()

VALID_CATEGORIES = ["时政", "财经", "科技", "娱乐", "体育", "美食", "教育", "其他"]
VALID_SORT = {"rank": HotTopic.rank, "heat": HotTopic.heat_value, "time": HotTopic.collected_at}


@router.get("/hot/list")
async def get_hot_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    category: str | None = Query(None),
    sort_by: str = Query("rank"),
    keyword: str | None = Query(None),
    session: AsyncSession = Depends(get_db),
):
    # Get latest batch
    latest_batch = await session.execute(
        select(HotTopic.batch_id).order_by(HotTopic.collected_at.desc()).limit(1)
    )
    batch_id = latest_batch.scalar_one_or_none()

    query = select(HotTopic)
    if batch_id:
        query = query.where(HotTopic.batch_id == batch_id)
    if category and category in VALID_CATEGORIES:
        query = query.where(HotTopic.category == category)
    if keyword:
        query = query.where(HotTopic.title.contains(keyword))

    sort_col = VALID_SORT.get(sort_by, HotTopic.rank)
    if sort_by == "rank":
        query = query.order_by(sort_col.asc())
    else:
        query = query.order_by(sort_col.desc())

    count_q = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await session.execute(query.offset(offset).limit(page_size))
    topics = result.scalars().all()

    items = [
        HotTopicItem(
            id=t.id, title=t.title, rank=t.rank, heat_value=t.heat_value,
            category=t.category, source=t.source,
            collected_at=t.collected_at.isoformat() if t.collected_at else None,
        )
        for t in topics
    ]

    return HotTopicListResponse(
        total=total, page=page, page_size=page_size, items=items,
        updated_at=topics[0].collected_at.isoformat() if topics else None,
    )


@router.get("/hot/{topic_id}")
async def get_hot_detail(
    topic_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(HotTopic).where(HotTopic.id == topic_id))
    topic = result.scalar_one_or_none()
    if not topic:
        return {"detail": "热点不存在"}, 404

    risk_level = None
    if topic.analysis:
        risk_level = topic.analysis.risk_level.value if topic.analysis.risk_level else None

    return HotTopicDetail(
        id=topic.id, title=topic.title, rank=topic.rank,
        heat_value=topic.heat_value, category=topic.category,
        source=topic.source, source_url=topic.source_url,
        summary=topic.summary, risk_level=risk_level,
        collected_at=topic.collected_at.isoformat() if topic.collected_at else None,
    )


@router.get("/hot/{topic_id}/analysis")
async def get_topic_analysis(
    topic_id: int,
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(TopicAnalysis).where(TopicAnalysis.topic_id == topic_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        return {"detail": "分析结果不存在"}, 404

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
