from abc import ABC, abstractmethod

from model.article import Article


class IFeedService(ABC):
    @abstractmethod
    async def post_articles(self, articles: list[Article]) -> None: ...
