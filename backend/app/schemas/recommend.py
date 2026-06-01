from pydantic import BaseModel


class RecommendItem(BaseModel):
    id: int
    topic_id: int
    topic_title: str
    topic_category: str | None = None
    topic_rank: int | None = None
    score: float
    reason: str
    match_tags: list[str] = []
    feedback: str | None = None


class RecommendListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    strategy: str | None = None
    items: list[RecommendItem]


class FeedbackRequest(BaseModel):
    recommend_id: int
    feedback: str  # liked / disliked


class ABStatsResponse(BaseModel):
    groups: list[dict]
