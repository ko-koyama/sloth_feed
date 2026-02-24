from abc import ABC, abstractmethod


class IScrapingService(ABC):
    @abstractmethod
    async def fetch_body(self, url: str) -> str: ...
