from unittest.mock import AsyncMock, MagicMock, patch

from service.zenn_scraping_service import BODY_MAX_LENGTH, ZennScrapingService


def _make_playwright_ctx(inner_text: str = "article body", element_found: bool = True):
    mock_element = AsyncMock()
    mock_element.inner_text = AsyncMock(return_value=inner_text)

    mock_page = AsyncMock()
    mock_page.goto = AsyncMock()
    mock_page.query_selector = AsyncMock(
        return_value=mock_element if element_found else None
    )

    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    mock_browser.close = AsyncMock()

    mock_p = MagicMock()
    mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_p)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    return mock_ctx, mock_page, mock_browser


async def test_fetch_body_returns_article_text():
    """セレクタにマッチした要素のテキストを返す"""
    mock_ctx, mock_page, _ = _make_playwright_ctx("article text")

    with patch("service.zenn_scraping_service.async_playwright", return_value=mock_ctx):
        service = ZennScrapingService()
        result = await service.fetch_body("https://zenn.dev/test/articles/abc")

    assert result == "article text"
    mock_page.goto.assert_awaited_once_with("https://zenn.dev/test/articles/abc")


async def test_fetch_body_returns_empty_when_element_not_found():
    """セレクタにマッチする要素がない場合は空文字を返す"""
    mock_ctx, _, _ = _make_playwright_ctx(element_found=False)

    with patch("service.zenn_scraping_service.async_playwright", return_value=mock_ctx):
        service = ZennScrapingService()
        result = await service.fetch_body("https://zenn.dev/test/articles/abc")

    assert result == ""


async def test_fetch_body_truncates_long_text():
    """本文が上限を超える場合は BODY_MAX_LENGTH 文字に切り詰める"""
    long_text = "x" * (BODY_MAX_LENGTH + 1000)
    mock_ctx, _, _ = _make_playwright_ctx(inner_text=long_text)

    with patch("service.zenn_scraping_service.async_playwright", return_value=mock_ctx):
        service = ZennScrapingService()
        result = await service.fetch_body("https://zenn.dev/test/articles/abc")

    assert len(result) == BODY_MAX_LENGTH


async def test_fetch_body_closes_browser_on_error():
    """ページ取得中に例外が発生しても browser.close が呼ばれる"""
    mock_page = AsyncMock()
    mock_page.goto = AsyncMock(side_effect=RuntimeError("network error"))

    mock_browser = AsyncMock()
    mock_browser.new_page = AsyncMock(return_value=mock_page)
    mock_browser.close = AsyncMock()

    mock_p = MagicMock()
    mock_p.chromium.launch = AsyncMock(return_value=mock_browser)

    mock_ctx = AsyncMock()
    mock_ctx.__aenter__ = AsyncMock(return_value=mock_p)
    mock_ctx.__aexit__ = AsyncMock(return_value=False)

    with patch("service.zenn_scraping_service.async_playwright", return_value=mock_ctx):
        import pytest

        service = ZennScrapingService()
        with pytest.raises(RuntimeError, match="network error"):
            await service.fetch_body("https://zenn.dev/test/articles/abc")

    mock_browser.close.assert_awaited_once()
