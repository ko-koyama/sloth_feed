from unittest.mock import AsyncMock, MagicMock

import discord

from model.article import Article
from service.discord_feed_service import DiscordFeedService


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
