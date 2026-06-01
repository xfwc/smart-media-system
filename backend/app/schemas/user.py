from pydantic import BaseModel


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    platform: str | None = None


class InterestRequest(BaseModel):
    category: str


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    interests: list[str] = []
    profile: dict | None = None

    model_config = {"from_attributes": True}
