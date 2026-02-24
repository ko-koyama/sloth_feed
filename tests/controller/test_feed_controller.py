from unittest.mock import AsyncMock

import pytest

from controller.feed_controller import FeedController
from model.article import Article


@pytest.fixture
def articles():
    return [
        Article(title="記事A", url="https://zenn.dev/a"),
        Article(title="記事B", url="https://zenn.dev/b"),
    ]


@pytest.fixture
def mock_article_service(articles):
    mock = AsyncMock()
    mock.get_articles.return_value = articles
    return mock


@pytest.fixture
def mock_feed_service():
    return AsyncMock()


@pytest.fixture
def mock_dedup_service(articles):
    mock = AsyncMock()
    mock.filter_unposted.return_value = articles
    return mock


async def test_run_passes_articles_to_feed_service(
    mock_article_service, mock_feed_service, mock_dedup_service, articles
):
    """get_articles の戻り値が dedup を経て post_articles に渡される"""
    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )
    await controller.run()

    mock_article_service.get_articles.assert_awaited_once()
    mock_dedup_service.filter_unposted.assert_awaited_once_with(articles)
    mock_feed_service.post_articles.assert_awaited_once_with(articles)


async def test_run_propagates_article_service_error(
    mock_feed_service, mock_dedup_service
):
    """get_articles 例外時、post_articles は呼ばれず例外が伝播する"""
    mock_article_service = AsyncMock()
    mock_article_service.get_articles.side_effect = RuntimeError("API error")

    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )

    with pytest.raises(RuntimeError, match="API error"):
        await controller.run()

    mock_feed_service.post_articles.assert_not_awaited()


async def test_run_posts_only_dedup_articles(
    mock_article_service, mock_feed_service, articles
):
    """dedup後の記事のみpostされる"""
    new_articles = [articles[0]]
    mock_dedup_service = AsyncMock()
    mock_dedup_service.filter_unposted.return_value = new_articles

    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )
    await controller.run()

    mock_feed_service.post_articles.assert_awaited_once_with(new_articles)


async def test_run_skips_post_when_no_new_articles(
    mock_article_service, mock_feed_service
):
    """新規記事なし→post未実行"""
    mock_dedup_service = AsyncMock()
    mock_dedup_service.filter_unposted.return_value = []

    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )
    await controller.run()

    mock_feed_service.post_articles.assert_not_awaited()


async def test_run_marks_as_posted_after_post(
    mock_article_service, mock_feed_service, mock_dedup_service, articles
):
    """post後にmark_as_postedが呼ばれる"""
    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )
    await controller.run()

    mock_feed_service.post_articles.assert_awaited_once()
    mock_dedup_service.mark_as_posted.assert_awaited_once_with(articles)


async def test_run_does_not_mark_posted_on_post_failure(
    mock_article_service, mock_dedup_service, articles
):
    """post失敗→mark_as_posted未実行"""
    mock_feed_service = AsyncMock()
    mock_feed_service.post_articles.side_effect = RuntimeError("Discord error")

    controller = FeedController(
        mock_article_service, mock_feed_service, mock_dedup_service
    )

    with pytest.raises(RuntimeError, match="Discord error"):
        await controller.run()

    mock_dedup_service.mark_as_posted.assert_not_awaited()
