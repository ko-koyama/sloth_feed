from unittest.mock import AsyncMock, MagicMock

import discord

from model.article import Article
from model.summary_result import SummaryResult
from service.discord_feed_service import CONTENT_MAX_LENGTH, DiscordFeedService


_UNSET = object()


def _make_service(
    channel: AsyncMock | None = None,
    get_channel_return: object = _UNSET,
) -> DiscordFeedService:
    mock_bot = MagicMock(spec=discord.Client)

    if get_channel_return is _UNSET:
        # get_channel が channel を返す（正常系）
        if channel is None:
            channel = AsyncMock()
        mock_bot.get_channel = MagicMock(return_value=channel)
    else:
        # get_channel が指定値(None等)を返す（フォールバック系）
        mock_bot.get_channel = MagicMock(return_value=get_channel_return)
        mock_bot.fetch_channel = AsyncMock(return_value=channel)

    return DiscordFeedService(mock_bot, channel_id=123), mock_bot, channel


async def test_creates_thread_for_each_article():
    """N記事 → N回 create_thread、名前とURLが正しい"""
    service, _, channel = _make_service()
    articles = [
        Article(title="記事A", url="https://zenn.dev/a"),
        Article(title="記事B", url="https://zenn.dev/b"),
    ]

    await service.post_articles(articles)

    assert channel.create_thread.await_count == 2
    channel.create_thread.assert_any_await(name="記事A", content="https://zenn.dev/a")
    channel.create_thread.assert_any_await(name="記事B", content="https://zenn.dev/b")


async def test_truncates_long_title():
    """150文字タイトル → 100文字に切り詰め"""
    service, _, channel = _make_service()
    long_title = "A" * 150
    articles = [Article(title=long_title, url="https://zenn.dev/x")]

    await service.post_articles(articles)

    channel.create_thread.assert_awaited_once_with(
        name="A" * 100, content="https://zenn.dev/x"
    )


async def test_falls_back_to_fetch_channel():
    """get_channel → None の場合 fetch_channel にフォールバック"""
    channel = AsyncMock()
    service, bot, _ = _make_service(channel=channel, get_channel_return=None)
    articles = [Article(title="記事", url="https://zenn.dev/x")]

    await service.post_articles(articles)

    bot.get_channel.assert_called_once_with(123)
    bot.fetch_channel.assert_awaited_once_with(123)
    channel.create_thread.assert_awaited_once()


async def test_content_includes_summary():
    """summary_result がある場合、content に箇条書きが含まれる"""
    service, _, channel = _make_service()
    article = Article(
        title="記事A",
        url="https://zenn.dev/a",
        summary_result=SummaryResult(summary=["ポイント1", "ポイント2"], glossary=None),
    )

    await service.post_articles([article])

    call_kwargs = channel.create_thread.call_args.kwargs
    content = call_kwargs["content"]
    assert "https://zenn.dev/a" in content
    assert "- ポイント1" in content
    assert "- ポイント2" in content
    assert "**要約**" in content


async def test_content_includes_glossary():
    """glossary がある場合、content に用語解説が含まれる"""
    service, _, channel = _make_service()
    article = Article(
        title="記事A",
        url="https://zenn.dev/a",
        summary_result=SummaryResult(
            summary=["ポイント1"],
            glossary=[
                {"term": "API", "explanation": "Application Programming Interface"}
            ],
        ),
    )

    await service.post_articles([article])

    call_kwargs = channel.create_thread.call_args.kwargs
    content = call_kwargs["content"]
    assert "**用語解説**" in content
    assert "**API**" in content
    assert "Application Programming Interface" in content


async def test_content_truncated_to_max_length():
    """content が上限を超える場合は 2000 文字に切り詰める"""
    service, _, channel = _make_service()
    article = Article(
        title="記事",
        url="https://zenn.dev/a",
        summary_result=SummaryResult(summary=["x" * 500] * 5, glossary=None),
    )

    await service.post_articles([article])

    call_kwargs = channel.create_thread.call_args.kwargs
    assert len(call_kwargs["content"]) <= CONTENT_MAX_LENGTH


async def test_content_without_summary_is_just_url():
    """summary_result がない場合、content は URL のみ"""
    service, _, channel = _make_service()
    article = Article(title="記事", url="https://zenn.dev/a")

    await service.post_articles([article])

    call_kwargs = channel.create_thread.call_args.kwargs
    assert call_kwargs["content"] == "https://zenn.dev/a"
