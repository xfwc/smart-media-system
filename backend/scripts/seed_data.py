"""Seed the database with users, templates, and ideas — no fake hot data."""
import asyncio, sys
sys.path.insert(0, '.')

from app.db.session import _get_engine
from app.core.security import get_password_hash
from app.models.user import User, UserProfile, UserInterest
from app.models.plan import PlanTemplate
from app.models.idea import Idea, IdeaStatus


async def seed():
    _, sessionmaker = _get_engine()
    async with sessionmaker() as session:
        # Users
        admin = User(username="admin", password_hash=get_password_hash("admin123"),
                     email="admin@smartmedia.com", role="admin")
        creator1 = User(username="creator1", password_hash=get_password_hash("creator123"),
                        email="creator1@test.com", role="creator")
        creator2 = User(username="creator2", password_hash=get_password_hash("creator123"),
                        role="creator")
        session.add_all([admin, creator1, creator2])
        await session.flush()

        session.add(UserProfile(user_id=creator1.id, nickname="创作者小王"))
        session.add(UserProfile(user_id=creator2.id, nickname="美食达人"))
        session.add(UserInterest(user_id=creator1.id, category="科技"))
        session.add(UserInterest(user_id=creator2.id, category="美食"))

        session.add_all([
            PlanTemplate(name="知识科普", description="通俗讲解专业知识",
                         style_tags=["教育"], prompt_template="科普模板"),
            PlanTemplate(name="新闻评论", description="深度评论分析",
                         style_tags=["评论"], prompt_template="评论模板"),
            PlanTemplate(name="生活教程", description="实用技能教学",
                         style_tags=["教程"], prompt_template="教程模板"),
        ])

        session.add_all([
            Idea(user_id=creator1.id, title="用动画解释大模型原理",
                 content="做3分钟动画短片...", category="科技", status=IdeaStatus.APPROVED),
            Idea(user_id=creator2.id, title="打卡夜市美食",
                 content="美食探店合集...", category="美食", status=IdeaStatus.APPROVED),
        ])

        await session.commit()
        print("[OK] Seed done: 3 users, 3 templates, 2 ideas")
        print("   Login: admin/admin123 | creator1/creator123 | creator2/creator123")


if __name__ == "__main__":
    asyncio.run(seed())
