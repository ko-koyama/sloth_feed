import httpx

from interface.i_article_service import IArticleService
from model.article import Article

ZENN_API_URL = "https://zenn.dev/api/articles"
ZENN_BASE_URL = "https://zenn.dev"
LIKED_COUNT_THRESHOLD = 50


class ZennArticleService(IArticleService):
    def __init__(self, article_type: str) -> None:
        self._article_type = article_type

    async def get_articles(self) -> list[Article]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                ZENN_API_URL,
                params={"order": "weekly", "page": 1},
            )
            response.raise_for_status()
            data = response.json()

        articles: list[Article] = []
        for item in data.get("articles", []):
            if item.get("article_type") != self._article_type:
                continue
            if item.get("liked_count", 0) < LIKED_COUNT_THRESHOLD:
                continue
            articles.append(
                Article(
                    title=item["title"],
                    url=f"{ZENN_BASE_URL}{item['path']}",
                )
            )

        return articles
