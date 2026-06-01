from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.schemas.user import ProfileUpdate, InterestRequest, UserProfileResponse
from app.services.user.user_service import (
    get_profile, update_profile, add_interest, remove_interest, list_interests,
)
from app.schemas.common import ApiResponse

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
