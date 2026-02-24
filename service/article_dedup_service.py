from interface.i_posted_article_repository import IPostedArticleRepository
from model.article import Article


class ArticleDedupService:
    def __init__(self, repository: IPostedArticleRepository) -> None:
        self._repository = repository

    async def filter_unposted(self, articles: list[Article]) -> list[Article]:
        unposted = []
        for article in articles:
            if not await self._repository.exists(article.url):
                unposted.append(article)
        return unposted

    async def mark_as_posted(self, articles: list[Article]) -> None:
        for article in articles:
            await self._repository.put(article)
