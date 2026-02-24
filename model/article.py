from dataclasses import dataclass

from model.summary_result import SummaryResult


@dataclass
class Article:
    title: str
    url: str
    summary_result: SummaryResult | None = None
