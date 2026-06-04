from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.core.deps import get_current_user_id, get_optional_user
from app.models.idea import Idea, IdeaLike, IdeaComment, IdeaStatus
from app.models.user import User
from app.models.hot import HotTopic
from app.schemas.idea import (
    IdeaCreateRequest, IdeaListResponse, IdeaItem, IdeaDetailResponse,
    CommentRequest, LikeResponse,
)
from app.schemas.common import ApiResponse

router = APIRouter()


@router.get("/ideas")
async def get_idea_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=20),
    category: str | None = None,
    sort_by: str = Query("hot"),
    keyword: str | None = None,
    session: AsyncSession = Depends(get_db),
):
    query = select(Idea).where(Idea.status == IdeaStatus.APPROVED)
    if category:
        query = query.where(Idea.category == category)
    if keyword:
        query = query.where(Idea.title.contains(keyword) | Idea.content.contains(keyword))

    count_q = select(func.count()).select_from(query.subquery())
    total = (await session.execute(count_q)).scalar() or 0

    if sort_by == "new":
        query = query.order_by(Idea.created_at.desc())
    else:
        query = query.order_by(Idea.likes_count.desc(), Idea.comments_count.desc())

    offset = (page - 1) * page_size
    result = await session.execute(query.offset(offset).limit(page_size))
    ideas = result.scalars().all()

    items = []
    for idea in ideas:
        author = "匿名用户" if idea.is_anonymous else ""
        if not idea.is_anonymous:
            user_result = await session.execute(select(User).where(User.id == idea.user_id))
            user = user_result.scalar_one_or_none()
            author = user.username if user else ""
        topic_title = None
        if idea.related_topic_id:
            t_result = await session.execute(select(HotTopic).where(HotTopic.id == idea.related_topic_id))
            t = t_result.scalar_one_or_none()
            topic_title = t.title if t else None

        items.append(IdeaItem(
            id=idea.id, title=idea.title,
            content_preview=idea.content[:200] if idea.content else "",
            category=idea.category, related_topic_title=topic_title,
            author_name=author, likes_count=idea.likes_count,
            comments_count=idea.comments_count,
            created_at=idea.created_at.isoformat() if idea.created_at else None,
        ))

    return IdeaListResponse(total=total, items=items)


@router.get("/ideas/{idea_id}")
async def get_idea_detail(
    idea_id: int,
    user_id: int | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    if not idea:
        return {"detail": "点子不存在"}, 404

    author_info = {"id": 0, "username": "匿名用户"}
    if not idea.is_anonymous:
        user_result = await session.execute(select(User).where(User.id == idea.user_id))
        user = user_result.scalar_one_or_none()
        if user:
            author_info = {"id": user.id, "username": user.username}

    # Check if current user liked
    liked_by_me = False
    if user_id:
        like_result = await session.execute(
            select(IdeaLike).where(IdeaLike.idea_id == idea_id, IdeaLike.user_id == user_id)
        )
        liked_by_me = like_result.scalar_one_or_none() is not None

    # Get comments
    comments_result = await session.execute(
        select(IdeaComment).where(IdeaComment.idea_id == idea_id)
        .order_by(IdeaComment.created_at.asc())
    )
    comments = comments_result.scalars().all()
    comment_list = []
    for c in comments:
        author = "匿名"
        u_result = await session.execute(select(User).where(User.id == c.user_id))
        u = u_result.scalar_one_or_none()
        if u:
            author = u.username
        comment_list.append({
            "id": c.id, "content": c.content, "author_name": author,
            "parent_id": c.parent_id,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "replies": [],
        })

    topic_title = None
    if idea.related_topic_id:
        t_result = await session.execute(select(HotTopic).where(HotTopic.id == idea.related_topic_id))
        t = t_result.scalar_one_or_none()
        topic_title = t.title if t else None

    return IdeaDetailResponse(
        id=idea.id, title=idea.title, content=idea.content,
        category=idea.category,
        tags=idea.tags if isinstance(idea.tags, list) else [],
        related_topic_id=idea.related_topic_id, related_topic_title=topic_title,
        author=author_info, likes_count=idea.likes_count, liked_by_me=liked_by_me,
        comments=comment_list, status=idea.status.value if idea.status else "pending",
        created_at=idea.created_at.isoformat() if idea.created_at else None,
    )


@router.post("/ideas", status_code=201)
async def create_idea(
    req: IdeaCreateRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    idea = Idea(
        user_id=user_id, title=req.title, content=req.content,
        category=req.category, tags=req.tags,
        related_topic_id=req.related_topic_id,
        is_anonymous=req.is_anonymous,
        status=IdeaStatus.PENDING,
    )
    session.add(idea)
    await session.flush()
    return {"id": idea.id, "status": "pending", "message": "点子已提交，审核通过后展示"}


@router.post("/ideas/{idea_id}/like")
async def toggle_like(
    idea_id: int,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    existing = await session.execute(
        select(IdeaLike).where(IdeaLike.idea_id == idea_id, IdeaLike.user_id == user_id)
    )
    like = existing.scalar_one_or_none()

    idea_result = await session.execute(select(Idea).where(Idea.id == idea_id))
    idea = idea_result.scalar_one_or_none()

    if like:
        await session.delete(like)
        if idea:
            idea.likes_count = max(0, idea.likes_count - 1)
        return LikeResponse(liked=False, likes_count=idea.likes_count if idea else 0)
    else:
        session.add(IdeaLike(idea_id=idea_id, user_id=user_id))
        if idea:
            idea.likes_count += 1
        return LikeResponse(liked=True, likes_count=idea.likes_count if idea else 1)


@router.post("/ideas/{idea_id}/comments", status_code=201)
async def create_comment(
    idea_id: int,
    req: CommentRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    comment = IdeaComment(
        idea_id=idea_id, user_id=user_id, content=req.content,
        parent_id=req.parent_id,
    )
    session.add(comment)

    idea_result = await session.execute(select(Idea).where(Idea.id == idea_id))
    idea = idea_result.scalar_one_or_none()
    if idea:
        idea.comments_count += 1

    await session.flush()
    return {
        "id": comment.id, "content": comment.content,
        "created_at": comment.created_at.isoformat() if comment.created_at else None,
    }
