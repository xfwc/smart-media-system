from pydantic import BaseModel, field_validator


class ProfileUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    platform: str | None = None


class InterestRequest(BaseModel):
    category: str


class PasswordChangeRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("新密码至少8位")
        return v


class UserProfileResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    interests: list[str] = []
    profile: dict | None = None

    model_config = {"from_attributes": True}
