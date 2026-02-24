from dataclasses import dataclass


@dataclass(frozen=True)
class SummaryResult:
    summary: list[str]
    glossary: list[dict[str, str]] | None
