import discord

from interface.i_feed_service import IFeedService
from model.article import Article

THREAD_NAME_MAX_LENGTH = 100


class DiscordFeedService(IFeedService):
    def __init__(self, bot: discord.Client, channel_id: int) -> None:
        self._bot = bot
        self._channel_id = channel_id

    async def post_articles(self, articles: list[Article]) -> None:
        channel = self._bot.get_channel(self._channel_id)
        if channel is None:
            channel = await self._bot.fetch_channel(self._channel_id)

        for article in articles:
            await channel.create_thread(
                name=article.title[:THREAD_NAME_MAX_LENGTH],
                content=article.url,
            )
