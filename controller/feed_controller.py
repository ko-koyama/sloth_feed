import logging

from interface.i_article_service import IArticleService
from interface.i_feed_service import IFeedService

logger = logging.getLogger(__name__)


class FeedController:
    def __init__(
        self,
        article_service: IArticleService,
        feed_service: IFeedService,
    ) -> None:
        self._article_service = article_service
        self._feed_service = feed_service

    async def run(self) -> None:
        logger.info("Starting feed task...")
        articles = await self._article_service.get_articles()
        logger.info("Fetched %d articles.", len(articles))
        await self._feed_service.post_articles(articles)
        logger.info("Feed posted.")
