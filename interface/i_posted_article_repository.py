from abc import ABC, abstractmethod

from model.article import Article


class IPostedArticleRepository(ABC):
    @abstractmethod
    async def exists(self, url: str) -> bool: ...

    @abstractmethod
    async def put(self, article: Article) -> None: ...
