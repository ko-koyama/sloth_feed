from abc import ABC, abstractmethod

from model.summary_result import SummaryResult


class ISummaryService(ABC):
    @abstractmethod
    async def summarize(self, title: str, body: str) -> SummaryResult: ...
