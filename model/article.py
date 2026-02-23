from dataclasses import dataclass


@dataclass(frozen=True)
class Article:
    title: str
    url: str
