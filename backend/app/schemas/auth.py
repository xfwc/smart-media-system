from pydantic import BaseModel, EmailStr, field_validator
import re


class RegisterRequest(BaseModel):
    username: str
    password: str
    email: str | None = None
    phone: str | None = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if len(v) < 3 or len(v) > 50:
            raise ValueError("用户名长度需在3-50个字符之间")
        if not re.match(r"^[a-zA-Z0-9_\-.]+$", v):
            raise ValueError("用户名只能包含字母、数字、下划线、点和连字符")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8 or len(v) > 128:
            raise ValueError("密码长度需在8-128个字符之间")
        return v

    @field_validator("email")
    @classmethod
    def validate_email_or_phone(cls, v: str | None, info) -> str | None:
        # Only validate format if provided
        if v is not None and "@" not in v:
            raise ValueError("邮箱格式不正确")
        return v


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    id: int
    username: str
    token: str
    interests: list[str] = []
    role: str | None = None
    message: str = ""


class UserResponse(BaseModel):
    id: int
    username: str
    email: str | None = None
    phone: str | None = None
    interests: list[str] = []
    created_at: str | None = None

    model_config = {"from_attributes": True}
