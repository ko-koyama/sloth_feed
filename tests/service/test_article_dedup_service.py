from unittest.mock import AsyncMock

import pytest

from model.article import Article
from service.article_dedup_service import ArticleDedupService


@pytest.fixture
def articles():
    return [
        Article(title="記事A", url="https://zenn.dev/a"),
        Article(title="記事B", url="https://zenn.dev/b"),
        Article(title="記事C", url="https://zenn.dev/c"),
    ]


async def test_filter_unposted_returns_only_unposted(articles):
    """投稿済みの記事を除いた未投稿記事のみ返す"""
    mock_repo = AsyncMock()
    mock_repo.exists.side_effect = [True, False, False]

    service = ArticleDedupService(mock_repo)
    result = await service.filter_unposted(articles)

    assert result == [articles[1], articles[2]]


async def test_filter_unposted_all_posted_returns_empty(articles):
    """全件投稿済みの場合は空リストを返す"""
    mock_repo = AsyncMock()
    mock_repo.exists.return_value = True

    service = ArticleDedupService(mock_repo)
    result = await service.filter_unposted(articles)

    assert result == []


async def test_filter_unposted_none_posted_returns_all(articles):
    """全件未投稿の場合は全件返す"""
    mock_repo = AsyncMock()
    mock_repo.exists.return_value = False

    service = ArticleDedupService(mock_repo)
    result = await service.filter_unposted(articles)

    assert result == articles


async def test_mark_as_posted_calls_put_for_each_article(articles):
    """各記事に対して put が呼ばれる"""
    mock_repo = AsyncMock()

    service = ArticleDedupService(mock_repo)
    await service.mark_as_posted(articles)

    assert mock_repo.put.await_count == len(articles)
    mock_repo.put.assert_any_await(articles[0])
    mock_repo.put.assert_any_await(articles[1])
    mock_repo.put.assert_any_await(articles[2])
