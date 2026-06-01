from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.deps import get_current_user_id
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserResponse
from app.schemas.user import UserProfileResponse
from app.services.user.auth_service import register, login
from app.services.user.user_service import get_profile

router = APIRouter()


@router.post("/auth/register", response_model=TokenResponse, status_code=201)
async def register_user(req: RegisterRequest, session: AsyncSession = Depends(get_db)):
    return await register(session, req)


@router.post("/auth/login", response_model=TokenResponse)
async def login_user(req: LoginRequest, session: AsyncSession = Depends(get_db)):
    return await login(session, req.username, req.password)


@router.get("/auth/me", response_model=UserProfileResponse)
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: AsyncSession = Depends(get_db),
):
    return await get_profile(session, user_id)
