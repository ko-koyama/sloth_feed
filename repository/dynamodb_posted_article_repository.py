import os
from datetime import datetime, timezone

import boto3

from interface.i_posted_article_repository import IPostedArticleRepository
from model.article import Article

AWS_REGION = os.environ.get("AWS_REGION", "ap-northeast-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "PostedArticles")


class DynamodbPostedArticleRepository(IPostedArticleRepository):
    def __init__(self, source: str) -> None:
        self._source = source
        dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)
        self._table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    async def exists(self, url: str) -> bool:
        response = self._table.get_item(Key={"url": url})
        return "Item" in response

    async def put(self, article: Article) -> None:
        posted_at = datetime.now(timezone.utc).isoformat()
        self._table.put_item(
            Item={
                "url": article.url,
                "title": article.title,
                "source": self._source,
                "posted_at": posted_at,
            }
        )
