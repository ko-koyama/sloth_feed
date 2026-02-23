from abc import ABC, abstractmethod

from model.article import Article


class IArticleService(ABC):
    @abstractmethod
    async def get_articles(self) -> list[Article]: ...
