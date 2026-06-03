from datetime import datetime
from sqlalchemy import String, DateTime, Integer, BigInteger, Text, Float, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models import Base
import enum


class Sentiment(str, enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class RiskLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class CrawlStatus(str, enum.Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


class HotTopic(Base):
    __tablename__ = "hot_topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    heat_value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    category: Mapped[str | None] = mapped_column(String(20))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(500))
    summary: Mapped[str | None] = mapped_column(Text)
    detail_text: Mapped[str | None] = mapped_column(Text)
    batch_id: Mapped[str] = mapped_column(String(36), nullable=False)
    collected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    analysis: Mapped["TopicAnalysis | None"] = relationship(back_populates="topic", uselist=False)


class TopicAnalysis(Base):
    __tablename__ = "topic_analysis"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("hot_topics.id"), unique=True)
    keywords: Mapped[dict] = mapped_column(JSON, nullable=False)
    category: Mapped[str] = mapped_column(String(20), nullable=False)
    sentiment: Mapped[Sentiment] = mapped_column(Enum(Sentiment), nullable=False)
    sentiment_score: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel), nullable=False)
    risk_reason: Mapped[str | None] = mapped_column(String(500))
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    topic: Mapped["HotTopic"] = relationship(back_populates="analysis")


class CrawlTask(Base):
    __tablename__ = "crawl_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    batch_id: Mapped[str | None] = mapped_column(String(36), unique=True)
    status: Mapped[CrawlStatus] = mapped_column(Enum(CrawlStatus), nullable=False)
    items_count: Mapped[int] = mapped_column(Integer, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime)


class HotTopicHistory(Base):
    __tablename__ = "hot_topic_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("hot_topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    heat_value: Mapped[int] = mapped_column(BigInteger, nullable=False)
    batch_id: Mapped[str] = mapped_column(String(36), nullable=False)
    snapshot_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
