"""Douyin hot list crawler via uapis.cn free API."""
import httpx
from loguru import logger

API_URL = "https://uapis.cn/api/v1/misc/hotboard?type=douyin"


async def fetch_douyin_hot() -> list[dict]:
    """Fetch Douyin hot list. Returns empty list on failure."""
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(API_URL, headers={"User-Agent": "Mozilla/5.0"})
            if resp.status_code != 200:
                logger.warning(f"API returned {resp.status_code}")
                return []

            data = resp.json()
            items = data.get("list", [])
            if not items:
                logger.warning("API returned empty list")
                return []

            results = []
            for item in items:
                results.append({
                    "rank": item.get("index", len(results) + 1),
                    "title": item.get("title", ""),
                    "hot_value": int(item.get("hot_value", 0) or 0),
                    "url": item.get("url", ""),
                    "label": item.get("label", item.get("tag", "热")),
                    "video_count": int(item.get("video_count", 0) or 0),
                    "view_count": int(item.get("view_count", 0) or 0),
                })

            logger.info(f"Fetched {len(results)} Douyin hot items")
            return results
    except Exception as e:
        logger.error(f"Fetch failed: {e}")
        return []
