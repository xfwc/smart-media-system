from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.core.security import get_password_hash, verify_password
from app.schemas.user import ProfileUpdate, InterestRequest, PasswordChangeRequest, UserProfileResponse
from app.services.user.user_service import (
    get_profile, update_profile, add_interest, remove_interest, list_interests,
)
from app.schemas.common import ApiResponse
from app.models.user import User
from sqlalchemy import select


from app.models.idea import Idea

router = APIRouter()


@router.get("/user/profile", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    return await get_profile(session, user_id)


@router.put("/user/profile")
async def update_user_profile(
    data: ProfileUpdate,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    await update_profile(session, user_id, data)
    return ApiResponse(message="资料更新成功")


@router.put("/user/password")
async def change_password(
    req: PasswordChangeRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="原密码错误")
    if req.old_password == req.new_password:
        raise HTTPException(status_code=400, detail="新密码不能和原密码一样")
    user.password_hash = get_password_hash(req.new_password)
    return ApiResponse(message="密码修改成功")


@router.get("/user/interests")
async def get_interests(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    interests = await list_interests(session, user_id)
    return ApiResponse(data=interests)


@router.post("/user/interests")
async def add_user_interest(
    req: InterestRequest,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    await add_interest(session, user_id, req.category)
    return ApiResponse(message="兴趣添加成功")


@router.delete("/user/interests/{category}")
async def remove_user_interest(
    category: str,
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    await remove_interest(session, user_id, category)
    return ApiResponse(message="兴趣已移除")


@router.get("/user/ideas")
async def get_my_ideas(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    result = await session.execute(
        select(Idea).where(Idea.user_id == user_id).order_by(Idea.created_at.desc())
    )
    ideas = result.scalars().all()
    return {
        "total": len(ideas),
        "items": [
            {
                "id": i.id,
                "title": i.title,
                "category": i.category,
                "status": i.status.value if i.status else "pending",
                "likes_count": i.likes_count,
                "comments_count": i.comments_count,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in ideas
        ],
    }
