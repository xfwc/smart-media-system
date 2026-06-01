from pydantic import BaseModel
from typing import TypeVar, Generic

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""
    code: int = 200
    message: str = "success"
    data: T | None = None


class PaginationParams(BaseModel):
    page: int = 1
    page_size: int = 20


class PaginatedResponse(BaseModel, Generic[T]):
    total: int
    page: int
    page_size: int
    items: list[T]


class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: str | None = None
