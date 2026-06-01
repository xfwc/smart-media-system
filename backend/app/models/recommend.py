from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Float, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base
import enum


class FeedbackEnum(str, enum.Enum):
    LIKED = "liked"
    DISLIKED = "disliked"


class ABAction(str, enum.Enum):
    IMPRESSION = "impression"
    CLICK = "click"
    LIKE = "like"
    DISLIKE = "dislike"


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("hot_topics.id"), nullable=False)
    strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    reason: Mapped[str] = mapped_column(String(200), nullable=False)
    match_tags: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RecommendationFeedback(Base):
    __tablename__ = "recommendation_feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    recommend_id: Mapped[int] = mapped_column(Integer, ForeignKey("recommendations.id"), unique=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    feedback: Mapped[FeedbackEnum] = mapped_column(Enum(FeedbackEnum), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ABExperiment(Base):
    __tablename__ = "ab_experiments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    strategy: Mapped[str] = mapped_column(String(20), nullable=False)
    traffic_ratio: Mapped[float] = mapped_column(Float, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime)


class ABImpression(Base):
    __tablename__ = "ab_impressions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    experiment_id: Mapped[int] = mapped_column(Integer, ForeignKey("ab_experiments.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    recommend_id: Mapped[int] = mapped_column(Integer, ForeignKey("recommendations.id"), nullable=False)
    action: Mapped[ABAction] = mapped_column(Enum(ABAction), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
