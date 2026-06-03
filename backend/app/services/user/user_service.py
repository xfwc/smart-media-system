from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.user import User, UserProfile, UserInterest
from app.schemas.user import ProfileUpdate, UserProfileResponse


async def get_profile(session: AsyncSession, user_id: int) -> UserProfileResponse:
    result = await session.execute(
        select(User).options(selectinload(User.profile)).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise ValueError("用户不存在")

    interests_result = await session.execute(
        select(UserInterest.category).where(UserInterest.user_id == user_id)
    )
    interests = [row[0] for row in interests_result.all()]

    profile = None
    if user.profile:
        profile = {
            "nickname": user.profile.nickname,
            "avatar_url": user.profile.avatar_url,
            "bio": user.profile.bio,
            "platform": user.profile.platform,
        }

    return UserProfileResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        phone=user.phone,
        interests=interests,
        profile=profile,
    )


async def update_profile(session: AsyncSession, user_id: int, data: ProfileUpdate):
    result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
    profile = result.scalar_one_or_none()
    if not profile:
        profile = UserProfile(user_id=user_id)
        session.add(profile)

    if data.nickname is not None:
        profile.nickname = data.nickname
    if data.avatar_url is not None:
        profile.avatar_url = data.avatar_url
    if data.bio is not None:
        profile.bio = data.bio
    if data.platform is not None:
        profile.platform = data.platform


async def add_interest(session: AsyncSession, user_id: int, category: str):
    existing = await session.execute(
        select(UserInterest).where(
            UserInterest.user_id == user_id, UserInterest.category == category
        )
    )
    if existing.scalar_one_or_none():
        raise ValueError("该分类已存在")
    interest = UserInterest(user_id=user_id, category=category)
    session.add(interest)


async def remove_interest(session: AsyncSession, user_id: int, category: str):
    await session.execute(
        delete(UserInterest).where(
            UserInterest.user_id == user_id, UserInterest.category == category
        )
    )


async def list_interests(session: AsyncSession, user_id: int) -> list[str]:
    result = await session.execute(
        select(UserInterest.category).where(UserInterest.user_id == user_id)
    )
    return [row[0] for row in result.all()]
