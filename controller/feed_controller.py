import logging

from interface.i_article_service import IArticleService
from interface.i_feed_service import IFeedService
from interface.i_scraping_service import IScrapingService
from interface.i_summary_service import ISummaryService
from service.article_dedup_service import ArticleDedupService

logger = logging.getLogger(__name__)


class FeedController:
    def __init__(
        self,
        article_service: IArticleService,
        feed_service: IFeedService,
        article_dedup_service: ArticleDedupService,
        scraping_service: IScrapingService,
        summary_service: ISummaryService,
    ) -> None:
        self._article_service = article_service
        self._feed_service = feed_service
        self._article_dedup_service = article_dedup_service
        self._scraping_service = scraping_service
        self._summary_service = summary_service

    async def run(self) -> None:
        logger.info("Starting feed task...")
        articles = await self._article_service.get_articles()
        logger.info("Fetched %d articles.", len(articles))
        new_articles = await self._article_dedup_service.filter_unposted(articles)
        logger.info("%d new articles after dedup.", len(new_articles))
        if not new_articles:
            logger.info("No new articles. Skipping post.")
            return

        for article in new_articles:
            try:
                body = await self._scraping_service.fetch_body(article.url)
                article.summary_result = await self._summary_service.summarize(
                    article.title, body
                )
            except Exception:
                logger.exception("Failed to summarize article: %s", article.url)

        await self._feed_service.post_articles(new_articles)
        await self._article_dedup_service.mark_as_posted(new_articles)
        logger.info("Feed posted.")
