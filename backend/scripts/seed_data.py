"""Seed the database with sample data for development and demo."""
import asyncio
import sys
sys.path.insert(0, '.')

from app.core.security import get_password_hash
from app.models.user import User, UserProfile, UserInterest
from app.models.hot import HotTopic, TopicAnalysis, Sentiment, RiskLevel
from app.models.plan import PlanTemplate
from app.models.idea import Idea, IdeaStatus
from app.db.session import AsyncSessionLocal

SAMPLE_TOPICS = [
    ("GPT-5发布引发AI行业震动", 1, 9800000, "科技"),
    ("2026高考作文题出炉", 2, 8750000, "教育"),
    ("某明星离婚案今日开庭", 3, 8200000, "娱乐"),
    ("全国多地迎来最强高温", 4, 7600000, "其他"),
    ("国足世预赛绝杀日本队", 5, 7200000, "体育"),
    ("央行宣布新一轮降息政策", 6, 6800000, "财经"),
    ("新型减肥药获FDA批准", 7, 6500000, "科技"),
    ("故宫博物院新展上线", 8, 6000000, "教育"),
    ("各地夜市经济持续火热", 9, 5800000, "美食"),
    ("新能源车销量再创新高", 10, 5500000, "财经"),
]

BATCH_ID = "seed-batch-20260529"


async def seed():
    async with AsyncSessionLocal() as session:
        # Users
        admin = User(
            username="admin", password_hash=get_password_hash("admin123"),
            email="admin@smartmedia.com", role="admin"
        )
        creator1 = User(
            username="creator1", password_hash=get_password_hash("creator123"),
            email="creator1@test.com", role="creator"
        )
        creator2 = User(
            username="creator2", password_hash=get_password_hash("creator123"),
            role="creator"
        )
        session.add_all([admin, creator1, creator2])
        await session.flush()

        # Profiles
        session.add(UserProfile(user_id=creator1.id, nickname="创作者小王", bio="热爱创作，专注科技内容"))
        session.add(UserProfile(user_id=creator2.id, nickname="美食达人", bio="分享各地美食"))

        # Interests
        session.add(UserInterest(user_id=creator1.id, category="科技", weight=1.0))
        session.add(UserInterest(user_id=creator1.id, category="财经", weight=0.8))
        session.add(UserInterest(user_id=creator2.id, category="美食", weight=1.0))
        session.add(UserInterest(user_id=creator2.id, category="娱乐", weight=0.6))

        # Hot topics with analysis
        for i, (title, rank, heat, cat) in enumerate(SAMPLE_TOPICS):
            topic = HotTopic(
                title=title, rank=rank, heat_value=heat, category=cat,
                source="douyin", source_url=f"https://example.com/{i}",
                summary=f"关于「{title}」的热点讨论",
                batch_id=BATCH_ID,
            )
            session.add(topic)
            await session.flush()

            # Analysis
            sentiments = [Sentiment.POSITIVE, Sentiment.NEUTRAL, Sentiment.POSITIVE,
                         Sentiment.NEUTRAL, Sentiment.POSITIVE, Sentiment.POSITIVE,
                         Sentiment.POSITIVE, Sentiment.POSITIVE, Sentiment.POSITIVE, Sentiment.POSITIVE]
            levels = [RiskLevel.LOW, RiskLevel.LOW, RiskLevel.MEDIUM,
                     RiskLevel.LOW, RiskLevel.LOW, RiskLevel.LOW,
                     RiskLevel.LOW, RiskLevel.LOW, RiskLevel.LOW, RiskLevel.LOW]

            analysis = TopicAnalysis(
                topic_id=topic.id,
                keywords=[cat, "热点", title[:4]],
                category=cat,
                sentiment=sentiments[i % len(sentiments)],
                sentiment_score=0.7 if sentiments[i % len(sentiments)] == Sentiment.POSITIVE else 0.2,
                risk_level=levels[i % len(levels)],
                risk_reason="内容客观公正" if levels[i % len(levels)] == RiskLevel.LOW else "涉及敏感话题，需注意措辞",
            )
            session.add(analysis)

        # Plan templates
        templates = [
            PlanTemplate(
                name="知识科普", description="以通俗易懂的方式讲解专业知识",
                style_tags=["教育", "科普", "干货"],
                prompt_template="请为「{{title}}」生成知识科普类视频企划...",
            ),
            PlanTemplate(
                name="新闻评论", description="对热点事件进行深度评论分析",
                style_tags=["评论", "观点", "深度"],
                prompt_template="请为「{{title}}」生成新闻评论类视频企划...",
            ),
            PlanTemplate(
                name="生活教程", description="手把手教观众实用技能",
                style_tags=["教程", "生活", "实用"],
                prompt_template="请为「{{title}}」生成生活教程类视频企划...",
            ),
        ]
        session.add_all(templates)

        # Sample ideas
        ideas = [
            Idea(user_id=creator1.id, title="用动画解释GPT-5的工作原理",
                 content="可以做一期3分钟的动画短片，用通俗语言解释大语言模型...",
                 category="科技", status=IdeaStatus.APPROVED, likes_count=15, comments_count=3),
            Idea(user_id=creator2.id, title="打卡全国10大夜市美食排行榜",
                 content="做一期美食探店合集，盘点国内最值得去的夜市...",
                 category="美食", status=IdeaStatus.APPROVED, likes_count=8, comments_count=1),
            Idea(user_id=creator1.id, title="深度分析：AI如何改变教育行业",
                 content="从K12到职业教育，AI正在重塑整个教育生态...",
                 category="教育", status=IdeaStatus.PENDING, likes_count=0, comments_count=0),
        ]
        session.add_all(ideas)

        await session.commit()
        print("✅ Seed data inserted successfully!")
        print(f"   Users: 3 (admin/creator1/creator2)")
        print(f"   Hot Topics: {len(SAMPLE_TOPICS)}")
        print(f"   Plan Templates: 3")
        print(f"   Ideas: 3")
        print(f"   Login: admin/admin123, creator1/creator123, creator2/creator123")


if __name__ == "__main__":
    asyncio.run(seed())
