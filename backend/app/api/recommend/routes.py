from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.models.recommend import Recommendation, RecommendationFeedback
from app.models.hot import HotTopic
from app.models.user import UserInterest
from app.schemas.recommend import RecommendItem, RecommendListResponse, FeedbackRequest
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/recommend")
async def get_recommendations(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=20),
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    # Get user interests
    interests_result = await session.execute(
        select(UserInterest.category).where(UserInterest.user_id == user_id)
    )
    interests = [r[0] for r in interests_result.all()]

    # Get topics from last 3 days
    since = datetime.utcnow() - timedelta(days=3)
    topics_result = await session.execute(
        select(HotTopic).where(HotTopic.collected_at >= since).order_by(HotTopic.heat_value.desc())
    )
    all_topics = list(topics_result.scalars().all())

    # Score each topic by interest match
    scored = []
    for t in all_topics:
        if interests and t.category in interests:
            score = 85
            reason = f"与你的「{t.category}」领域高度匹配"
        elif interests and t.category:
            score = 50
            reason = f"跨领域热点，扩展创作视野"
        else:
            score = 30
            reason = "当前热门话题，值得关注"

        # Heat bonus
        max_heat = max(t.heat_value for t in all_topics) or 1
        score += (t.heat_value / max_heat) * 10

        scored.append((t, min(100, round(score, 1)), reason))

    scored.sort(key=lambda x: x[1], reverse=True)
    total = len(scored)

    start = (page - 1) * page_size
    items = [
        RecommendItem(
            id=0,
            topic_id=t.id,
            topic_title=t.title,
            topic_category=t.category,
            topic_rank=idx + 1,
            score=s,
            reason=r,
            match_tags=[t.category] if t.category else [],
        )
        for idx, (t, s, r) in enumerate(scored[start : start + page_size])
    ]

    return RecommendListResponse(
        total=total, page=page, page_size=page_size,
        strategy="interest_match", items=items,
    )


@router.post("/recommend/feedback")
async def submit_feedback(
    req: FeedbackRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    existing = await session.execute(
        select(RecommendationFeedback).where(
            RecommendationFeedback.recommend_id == req.recommend_id
        )
    )
    fb = existing.scalar_one_or_none()
    if fb:
        fb.feedback = req.feedback
    else:
        fb = RecommendationFeedback(
            recommend_id=req.recommend_id, user_id=user_id, feedback=req.feedback,
        )
        session.add(fb)
    return ApiResponse(message="反馈已提交")


@router.get("/recommend/history")
async def get_recommend_history(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Recommendation).where(Recommendation.user_id == user_id)
        .order_by(Recommendation.created_at.desc()).limit(50)
    )
    recs = result.scalars().all()
    items = []
    for r in recs:
        topic_result = await session.execute(select(HotTopic).where(HotTopic.id == r.topic_id))
        topic = topic_result.scalar_one_or_none()
        items.append({
            "id": r.id, "topic_title": topic.title if topic else "",
            "score": r.score, "created_at": r.created_at.isoformat() if r.created_at else None,
        })
    return {"total": len(items), "items": items}
