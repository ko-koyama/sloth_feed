import logging

from interface.i_article_service import IArticleService
from interface.i_feed_service import IFeedService
from service.article_dedup_service import ArticleDedupService

logger = logging.getLogger(__name__)


class FeedController:
    def __init__(
        self,
        article_service: IArticleService,
        feed_service: IFeedService,
        article_dedup_service: ArticleDedupService,
    ) -> None:
        self._article_service = article_service
        self._feed_service = feed_service
        self._article_dedup_service = article_dedup_service

    async def run(self) -> None:
        logger.info("Starting feed task...")
        articles = await self._article_service.get_articles()
        logger.info("Fetched %d articles.", len(articles))
        new_articles = await self._article_dedup_service.filter_unposted(articles)
        logger.info("%d new articles after dedup.", len(new_articles))
        if not new_articles:
            logger.info("No new articles. Skipping post.")
            return
        await self._feed_service.post_articles(new_articles)
        await self._article_dedup_service.mark_as_posted(new_articles)
        logger.info("Feed posted.")
