import datetime
import logging
import os

import discord
from discord.ext import tasks
from dotenv import load_dotenv

from controller.feed_controller import FeedController
from service.discord_feed_service import DiscordFeedService
from service.zenn_article_service import ZennArticleService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# JST 9:00 = UTC 0:00, JST 18:00 = UTC 9:00
SCHEDULE_TIMES = [
    datetime.time(hour=0, minute=0),
    datetime.time(hour=9, minute=0),
]

intents = discord.Intents.default()
bot = discord.Client(intents=intents)


def _build_controller() -> FeedController:
    article_service = ZennArticleService()
    channel_id = int(os.environ["DISCORD_CHANNEL_ID_ZENN"])
    feed_service = DiscordFeedService(bot, channel_id)
    return FeedController(article_service, feed_service)


@tasks.loop(time=SCHEDULE_TIMES)
async def scheduled_feed_task() -> None:
    logger.info("Scheduled feed task triggered.")
    controller = _build_controller()
    await controller.run()


@bot.event
async def on_ready() -> None:
    logger.info("Bot is ready. Logged in as %s", bot.user)
    if not scheduled_feed_task.is_running():
        scheduled_feed_task.start()


def main() -> None:
    load_dotenv()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    if not token:
        raise RuntimeError("DISCORD_BOT_TOKEN environment variable is not set.")
    bot.run(token)


if __name__ == "__main__":
    main()
