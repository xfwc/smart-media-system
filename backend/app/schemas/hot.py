from pydantic import BaseModel
from datetime import datetime


class HotTopicItem(BaseModel):
    id: int
    title: str
    rank: int
    heat_value: int
    category: str | None = None
    source: str
    collected_at: str | None = None

    model_config = {"from_attributes": True}


class HotTopicListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[HotTopicItem]
    updated_at: str | None = None


class HotTopicDetail(BaseModel):
    id: int
    title: str
    rank: int
    heat_value: int
    category: str | None = None
    source: str
    source_url: str | None = None
    summary: str | None = None
    detail_text: str | None = None
    risk_level: str | None = None
    collected_at: str | None = None

    model_config = {"from_attributes": True}


class TopicAnalysisResponse(BaseModel):
    topic_id: int
    keywords: list[str]
    category: str
    sentiment: str
    sentiment_score: float
    risk_level: str
    risk_reason: str | None = None
    analyzed_at: str | None = None

    model_config = {"from_attributes": True}
