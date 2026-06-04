from datetime import datetime
from sqlalchemy import String, DateTime, Integer, Text, Boolean, JSON, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column
from app.models import Base
import enum


class PlanStatus(str, enum.Enum):
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class PlanTemplate(Base):
    __tablename__ = "plan_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    style_tags: Mapped[dict] = mapped_column(JSON, nullable=False)
    prompt_template: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class ContentPlan(Base):
    __tablename__ = "content_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(Integer, ForeignKey("hot_topics.id"), nullable=False)
    template_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("plan_templates.id"))
    status: Mapped[PlanStatus] = mapped_column(Enum(PlanStatus), nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PlanIntent(Base):
    __tablename__ = "plan_intents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_plans.id"), unique=True)
    angle: Mapped[str | None] = mapped_column(Text)
    audience: Mapped[str | None] = mapped_column(Text)
    style: Mapped[str | None] = mapped_column(String(50))


class PlanOutput(Base):
    __tablename__ = "plan_outputs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_plans.id"), unique=True)
    title_suggestions: Mapped[dict] = mapped_column(JSON, nullable=False)
    outline: Mapped[dict] = mapped_column(JSON, nullable=False)
    shooting_advice: Mapped[str | None] = mapped_column(Text)
    publish_advice: Mapped[str | None] = mapped_column(Text)
    recommended_tags: Mapped[dict | None] = mapped_column(JSON)
    risk_warning: Mapped[str | None] = mapped_column(Text)
    raw_ai_response: Mapped[str | None] = mapped_column(Text)


class PlanHistoryVersion(Base):
    __tablename__ = "plan_history_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("content_plans.id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    plan_output_id: Mapped[int] = mapped_column(Integer, ForeignKey("plan_outputs.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
