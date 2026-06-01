from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.models.user import User, UserRole
from app.models.idea import Idea, IdeaStatus, ReviewRecord, ReviewAction
from app.models.hot import HotTopic
from app.models.recommend import Recommendation
from app.models.plan import ContentPlan
from app.schemas.common import ApiResponse

router = APIRouter()


async def require_admin(user_id: int, session: AsyncSession):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or user.role.value == "creator":
        return False
    return True


@router.get("/admin/ideas/pending")
async def get_pending_ideas(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    if not await require_admin(user_id, session):
        return ApiResponse(code=403, message="无权限"), 403

    result = await session.execute(
        select(Idea).where(Idea.status == IdeaStatus.PENDING).order_by(Idea.created_at.desc())
    )
    ideas = result.scalars().all()
    items = []
    for idea in ideas:
        user_result = await session.execute(select(User).where(User.id == idea.user_id))
        author = user_result.scalar_one_or_none()
        items.append({
            "id": idea.id, "title": idea.title, "content": idea.content[:300],
            "category": idea.category, "author": author.username if author else "未知",
            "created_at": idea.created_at.isoformat() if idea.created_at else None,
        })
    return {"total": len(items), "items": items}


@router.post("/admin/ideas/{idea_id}/review")
async def review_idea(
    idea_id: int,
    action: str,
    reason: str = "",
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    if not await require_admin(user_id, session):
        return ApiResponse(code=403, message="无权限"), 403

    result = await session.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        return ApiResponse(code=404, message="点子不存在"), 404

    if action == "approve":
        idea.status = IdeaStatus.APPROVED
    elif action == "reject":
        idea.status = IdeaStatus.REJECTED
    else:
        return ApiResponse(code=400, message="无效操作"), 400

    record = ReviewRecord(
        idea_id=idea_id,
        reviewer_id=user_id,
        action=ReviewAction.APPROVE if action == "approve" else ReviewAction.REJECT,
        reason=reason if action == "reject" else None,
    )
    session.add(record)
    return ApiResponse(message="审核完成")


@router.get("/admin/stats")
async def get_admin_stats(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    if not await require_admin(user_id, session):
        return ApiResponse(code=403, message="无权限"), 403

    users_total = (await session.execute(select(func.count(User.id)))).scalar() or 0
    topics_total = (await session.execute(select(func.count(HotTopic.id)))).scalar() or 0
    recs_total = (await session.execute(select(func.count(Recommendation.id)))).scalar() or 0
    plans_total = (await session.execute(select(func.count(ContentPlan.id)))).scalar() or 0
    ideas_total = (await session.execute(select(func.count(Idea.id)))).scalar() or 0

    return {
        "users_total": users_total, "topics_total": topics_total,
        "recommendations_total": recs_total, "plans_total": plans_total,
        "ideas_total": ideas_total, "daily_active_users": 0,
        "stats_by_date": [],
    }
