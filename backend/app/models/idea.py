from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, Boolean, JSON, Float, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base
import enum


class IdeaStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ReviewAction(str, enum.Enum):
    APPROVE = "approve"
    REJECT = "reject"


class Idea(Base):
    __tablename__ = "ideas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    tags: Mapped[dict | None] = mapped_column(JSON)
    related_topic_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("hot_topics.id"))
    is_anonymous: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[IdeaStatus] = mapped_column(Enum(IdeaStatus), default=IdeaStatus.PENDING)
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class IdeaLike(Base):
    __tablename__ = "idea_likes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idea_id: Mapped[int] = mapped_column(Integer, ForeignKey("ideas.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdeaComment(Base):
    __tablename__ = "idea_comments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idea_id: Mapped[int] = mapped_column(Integer, ForeignKey("ideas.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("idea_comments.id"))
    content: Mapped[str] = mapped_column(String(500), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class ReviewRecord(Base):
    __tablename__ = "review_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idea_id: Mapped[int] = mapped_column(Integer, ForeignKey("ideas.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    action: Mapped[ReviewAction] = mapped_column(Enum(ReviewAction), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500))
    reviewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class IdeaHotScore(Base):
    __tablename__ = "idea_hot_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    idea_id: Mapped[int] = mapped_column(Integer, ForeignKey("ideas.id"), unique=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    likes_weight: Mapped[float] = mapped_column(Float, nullable=False)
    comments_weight: Mapped[float] = mapped_column(Float, nullable=False)
    time_decay: Mapped[float] = mapped_column(Float, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
