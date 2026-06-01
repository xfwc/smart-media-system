from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
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

    # Content-based: match by category
    query = select(Recommendation).where(Recommendation.user_id == user_id)
    count_q = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_q)).scalar() or 0

    offset = (page - 1) * page_size
    result = await session.execute(query.order_by(Recommendation.score.desc()).offset(offset).limit(page_size))
    recs = result.scalars().all()

    items = []
    for r in recs:
        topic_result = await session.execute(select(HotTopic).where(HotTopic.id == r.topic_id))
        topic = topic_result.scalar_one_or_none()
        fb_result = await session.execute(
            select(RecommendationFeedback).where(RecommendationFeedback.recommend_id == r.id)
        )
        fb = fb_result.scalar_one_or_none()

        items.append(RecommendItem(
            id=r.id,
            topic_id=r.topic_id,
            topic_title=topic.title if topic else "",
            topic_category=topic.category if topic else None,
            topic_rank=topic.rank if topic else None,
            score=r.score,
            reason=r.reason,
            match_tags=r.match_tags if isinstance(r.match_tags, list) else [],
            feedback=fb.feedback.value if fb else None,
        ))

    return RecommendListResponse(
        total=total, page=page, page_size=page_size,
        strategy="mixed", items=items,
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
