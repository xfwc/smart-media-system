"""Douyin hot ranking data model."""
from datetime import datetime
from sqlalchemy import String, DateTime, Integer, BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base


class HotRanking(Base):
    __tablename__ = "hot_rankings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    hot_value: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    url: Mapped[str | None] = mapped_column(String(1000))
    label: Mapped[str | None] = mapped_column(String(50))
    video_count: Mapped[int | None] = mapped_column(Integer)
    view_count: Mapped[int | None] = mapped_column(BigInteger)
    crawled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("rank", "crawled_at", name="uq_rank_crawled"),)
