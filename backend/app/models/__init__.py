from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.models.user import User, UserProfile, UserInterest, UserBehaviorLog
from app.models.hot import HotTopic, TopicAnalysis, CrawlTask, HotTopicHistory
from app.models.hot_models import HotRanking
from app.models.recommend import Recommendation, RecommendationFeedback, ABExperiment, ABImpression
from app.models.plan import ContentPlan, PlanIntent, PlanOutput, PlanTemplate, PlanHistoryVersion
from app.models.idea import Idea, IdeaLike, IdeaComment, ReviewRecord, IdeaHotScore
