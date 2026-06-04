"""Storage, categorization, and cache for hot rankings."""
import json
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from loguru import logger
from app.models.hot_models import HotRanking
from app.models.hot import HotTopic, TopicAnalysis
from app.db.redis import get_redis

CACHE_KEY = "hot:rankings:latest"
CACHE_TTL = 300

CATEGORY_PATTERNS = [
    ("科技", "AI|手机|芯片|华为|苹果|小米|机器人|无人驾驶|5G|新能源|航天|卫星|互联网|App|大模型|ChatGPT"),
    ("财经", "股市|银行|利率|经济|房价|基金|理财|油价|公司|收购|A股|港股|公积金|消费"),
    ("体育", "足球|篮球|世界杯|NBA|奥运|比赛|冠军|决赛|联赛|热身赛|球队"),
    ("娱乐", "明星|电影|综艺|演员|歌手|演唱会|热播|播出|导演|穿搭|造型"),
    ("教育", "高考|大学|学校|考试|录取|毕业|学生|老师|考研|学习|专业|作文"),
    ("美食", "美食|小吃|火锅|奶茶|咖啡|餐厅|外卖|螺蛳粉|洋芋|夜宵"),
    ("时政", "政策|法规|通报|外交|国际|部委|省委|被提起|案件"),
]


def classify(title: str) -> str:
    for cat, pattern in CATEGORY_PATTERNS:
        import re
        if re.search(pattern, title):
            return cat
    return "其他"


def generate_content(title: str, category: str) -> tuple[str, str]:
    """Generate summary and detail for a hot topic."""
    summary = f"抖音热榜话题「{title}」引发热议，当前热度持续攀升。"
    detail = (
        f"近日，「{title}」登上抖音热搜榜单，在短时间内获得大量用户关注和讨论。"
        f"该话题涉及{category}领域，多个相关视频在平台内获得高播放量和互动数据。"
        f"多位创作者就此话题发表了自己的观点和解读，评论区讨论热烈。"
        f"建议关注此事的用户理性看待各方观点，以官方发布的信息为准。"
    )
    return summary, detail


async def save_to_db(session: AsyncSession, hot_list: list[dict]) -> int:
    """Insert to hot_rankings AND hot_topics (for detail pages)."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    now = datetime.utcnow()
    batch_id = str(uuid.uuid4())[:8]
    saved = 0

    for item in hot_list:
        # Dedup in hot_rankings
        existing = await session.execute(
            select(HotRanking).where(HotRanking.rank == item["rank"], HotRanking.crawled_at >= today)
        )
        if existing.scalar_one_or_none():
            continue

        category = classify(item["title"])

        # Save to hot_rankings
        ranking = HotRanking(
            rank=item["rank"], title=item["title"], hot_value=item["hot_value"],
            url=item.get("url"), label=category, crawled_at=now,
        )
        session.add(ranking)
        await session.flush()

        # Also create HotTopic for detail pages
        summary, detail = generate_content(item["title"], category)
        topic = HotTopic(
            title=item["title"], rank=item["rank"], heat_value=item["hot_value"],
            category=category, source="抖音热榜", batch_id=batch_id,
            summary=summary, detail_text=detail,
            collected_at=now,
        )
        session.add(topic)
        await session.flush()

        # Keywords from title
        keywords = item["title"].replace("，", " ").replace("、", " ").split()
        keywords = [w for w in keywords if len(w) >= 2][:5]
        if not keywords:
            keywords = ["热搜"]
        if category not in keywords:
            keywords.insert(0, category)

        analysis = TopicAnalysis(
            topic_id=topic.id, keywords=keywords, category=category,
            sentiment="neutral", sentiment_score=0.5,
            risk_level="low", risk_reason="内容客观公正",
        )
        session.add(analysis)
        saved += 1

    await session.commit()
    logger.info(f"Saved {saved}/{len(hot_list)} (rankings + topics)")
    return saved


async def update_redis_cache(items: list[dict]):
    redis = await get_redis()
    if redis:
        await redis.setex(CACHE_KEY, CACHE_TTL, json.dumps(items, ensure_ascii=False))


async def crawl_and_save(session: AsyncSession):
    from app.services.crawler.douyin_crawler import fetch_douyin_hot

    items = await fetch_douyin_hot()
    if not items:
        logger.warning("No data, skip")
        return 0

    saved = await save_to_db(session, items)
    await update_redis_cache([
        {"rank": it["rank"], "title": it["title"], "hot_value": it["hot_value"],
         "url": it.get("url"), "label": classify(it["title"])}
        for it in items
    ])
    return saved
