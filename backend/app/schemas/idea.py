from pydantic import BaseModel


class IdeaCreateRequest(BaseModel):
    title: str
    content: str
    category: str
    tags: list[str] | None = None
    related_topic_id: int | None = None
    is_anonymous: bool = False


class IdeaListResponse(BaseModel):
    total: int
    items: list["IdeaItem"]


class IdeaItem(BaseModel):
    id: int
    title: str
    content_preview: str = ""
    category: str
    related_topic_title: str | None = None
    author_name: str = ""
    likes_count: int = 0
    comments_count: int = 0
    created_at: str | None = None


class CommentRequest(BaseModel):
    content: str
    parent_id: int | None = None


class LikeResponse(BaseModel):
    liked: bool
    likes_count: int


class IdeaDetailResponse(BaseModel):
    id: int
    title: str
    content: str
    category: str
    tags: list[str] = []
    related_topic_id: int | None = None
    related_topic_title: str | None = None
    author: dict | None = None
    likes_count: int = 0
    liked_by_me: bool = False
    comments: list[dict] = []
    status: str = "pending"
    created_at: str | None = None
