"""Unit tests for Douyin crawler and storage."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime


class TestFetchDouyinHot:
    @pytest.mark.asyncio
    async def test_api_success(self):
        """Mock httpx to return valid hot list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "list": [
                {"index": 1, "title": "Test Hot 1", "hot_value": 1000000, "url": "https://test.com/1", "label": "热"},
                {"index": 2, "title": "Test Hot 2", "hot_value": 900000, "url": "https://test.com/2", "label": "新"},
            ]
        }

        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            from app.services.crawler.douyin_crawler import fetch_douyin_hot
            items = await fetch_douyin_hot()

        assert len(items) == 2
        assert items[0]["title"] == "Test Hot 1"
        assert items[0]["rank"] == 1
        assert items[1]["label"] == "新"

    @pytest.mark.asyncio
    async def test_api_failure(self):
        """API failure returns empty list."""
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, side_effect=Exception("Network error")):
            from app.services.crawler.douyin_crawler import fetch_douyin_hot
            items = await fetch_douyin_hot()
        assert items == []

    @pytest.mark.asyncio
    async def test_api_empty(self):
        """Empty response returns empty list."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"list": []}
        with patch("httpx.AsyncClient.get", new_callable=AsyncMock, return_value=mock_resp):
            from app.services.crawler.douyin_crawler import fetch_douyin_hot
            items = await fetch_douyin_hot()
        assert items == []


class TestSaveToDb:
    @pytest.mark.asyncio
    async def test_dedup(self):
        """Same rank+crawled_at date should be skipped."""
        mock_session = AsyncMock()
        # First call: no existing row
        mock_session.execute = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        from app.services.crawler.hot_service import save_to_db
        items = [{"rank": 1, "title": "Test", "hot_value": 100}]
        saved = await save_to_db(mock_session, items)
        assert saved == 1

        # Second call: row exists
        mock_result.scalar_one_or_none.return_value = MagicMock()
        saved2 = await save_to_db(mock_session, items)
        assert saved2 == 0
