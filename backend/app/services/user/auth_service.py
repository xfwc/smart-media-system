from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import RegisterRequest, TokenResponse


async def register(session: AsyncSession, req: RegisterRequest) -> TokenResponse:
    # Check uniqueness
    existing = await session.execute(select(User).where(User.username == req.username))
    if existing.scalar_one_or_none():
        raise ValueError("用户名已存在")
    if req.email:
        existing = await session.execute(select(User).where(User.email == req.email))
        if existing.scalar_one_or_none():
            raise ValueError("邮箱已被注册")
    if req.phone:
        existing = await session.execute(select(User).where(User.phone == req.phone))
        if existing.scalar_one_or_none():
            raise ValueError("手机号已被注册")

    user = User(
        username=req.username,
        password_hash=get_password_hash(req.password),
        email=req.email,
        phone=req.phone,
    )
    session.add(user)
    await session.flush()

    token = create_access_token(user.id)
    return TokenResponse(
        id=user.id,
        username=user.username,
        token=token,
        message="注册成功",
    )


async def login(session: AsyncSession, username: str, password: str) -> TokenResponse:
    result = await session.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise ValueError("用户名或密码错误")
    if not user.is_active:
        raise ValueError("账号已被禁用")

    # Load interests
    from app.models.user import UserInterest
    interests_result = await session.execute(
        select(UserInterest.category).where(UserInterest.user_id == user.id)
    )
    interests = [row[0] for row in interests_result.all()]

    token = create_access_token(user.id)
    return TokenResponse(
        id=user.id,
        username=user.username,
        token=token,
        interests=interests,
        role=user.role.value if user.role else None,
    )
