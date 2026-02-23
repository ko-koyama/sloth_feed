from unittest.mock import AsyncMock

import pytest

from controller.feed_controller import FeedController
from model.article import Article


async def test_run_passes_articles_to_feed_service():
    """get_articles の戻り値が post_articles に渡される"""
    articles = [
        Article(title="記事A", url="https://zenn.dev/a"),
        Article(title="記事B", url="https://zenn.dev/b"),
    ]
    mock_article_service = AsyncMock()
    mock_article_service.get_articles.return_value = articles
    mock_feed_service = AsyncMock()

    controller = FeedController(mock_article_service, mock_feed_service)
    await controller.run()

    mock_article_service.get_articles.assert_awaited_once()
    mock_feed_service.post_articles.assert_awaited_once_with(articles)


async def test_run_propagates_article_service_error():
    """get_articles 例外時、post_articles は呼ばれず例外が伝播する"""
    mock_article_service = AsyncMock()
    mock_article_service.get_articles.side_effect = RuntimeError("API error")
    mock_feed_service = AsyncMock()

    controller = FeedController(mock_article_service, mock_feed_service)

    with pytest.raises(RuntimeError, match="API error"):
        await controller.run()

    mock_feed_service.post_articles.assert_not_awaited()
