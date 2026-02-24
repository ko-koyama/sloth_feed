import boto3
import pytest
from moto import mock_aws

from model.article import Article
from repository.dynamodb_posted_article_repository import (
    DynamodbPostedArticleRepository,
)

TABLE_NAME = "PostedArticles"
REGION = "ap-northeast-1"


@pytest.fixture(autouse=True)
def aws_env(monkeypatch):
    monkeypatch.setenv("AWS_REGION", REGION)
    monkeypatch.setenv("DYNAMODB_TABLE_NAME", TABLE_NAME)
    monkeypatch.setenv("AWS_DEFAULT_REGION", REGION)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name=REGION)
        table = dynamodb.create_table(
            TableName=TABLE_NAME,
            KeySchema=[{"AttributeName": "url", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "url", "AttributeType": "S"}],
            BillingMode="PAY_PER_REQUEST",
        )
        yield table


async def test_exists_returns_false_when_not_posted(dynamodb_table):
    """未投稿のURLに対して False を返す"""
    repo = DynamodbPostedArticleRepository("zenn_tech")
    result = await repo.exists("https://zenn.dev/a")
    assert result is False


async def test_exists_returns_true_after_put(dynamodb_table):
    """put 後に exists が True を返す"""
    repo = DynamodbPostedArticleRepository("zenn_tech")
    article = Article(title="記事A", url="https://zenn.dev/a")

    await repo.put(article)
    result = await repo.exists(article.url)

    assert result is True


async def test_put_saves_source_and_posted_at(dynamodb_table):
    """put で source と posted_at が保存される"""
    repo = DynamodbPostedArticleRepository("zenn_tech")
    article = Article(title="記事A", url="https://zenn.dev/a")

    await repo.put(article)

    response = dynamodb_table.get_item(Key={"url": article.url})
    item = response["Item"]
    assert item["title"] == "記事A"
    assert item["source"] == "zenn_tech"
    assert "posted_at" in item
