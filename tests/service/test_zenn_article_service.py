import httpx
import respx

from model.article import Article
from service.zenn_article_service import (
    ZENN_API_URL,
    ZennArticleService,
)


def _make_item(
    title: str = "記事",
    path: str = "/user/articles/1",
    article_type: str = "tech",
    liked_count: int = 100,
) -> dict:
    return {
        "title": title,
        "path": path,
        "article_type": article_type,
        "liked_count": liked_count,
    }


@respx.mock
async def test_returns_tech_articles():
    """article_type=tech かつ liked_count>=50 の記事のみ返る"""
    respx.get(ZENN_API_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "articles": [
                    _make_item(title="Tech記事A", article_type="tech", liked_count=80),
                    _make_item(title="Tech記事B", article_type="tech", liked_count=60),
                    _make_item(title="除外:idea", article_type="idea", liked_count=200),
                    _make_item(
                        title="除外:少ない", article_type="tech", liked_count=10
                    ),
                ]
            },
        )
    )

    articles = await ZennArticleService("tech").get_articles()

    assert len(articles) == 2
    assert articles[0] == Article(
        title="Tech記事A", url="https://zenn.dev/user/articles/1"
    )
    assert articles[1] == Article(
        title="Tech記事B", url="https://zenn.dev/user/articles/1"
    )


@respx.mock
async def test_returns_idea_articles():
    """article_type=idea かつ liked_count>=50 の記事のみ返る"""
    respx.get(ZENN_API_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "articles": [
                    _make_item(title="Idea記事A", article_type="idea", liked_count=80),
                    _make_item(title="除外:tech", article_type="tech", liked_count=200),
                    _make_item(
                        title="除外:少ない", article_type="idea", liked_count=10
                    ),
                ]
            },
        )
    )

    articles = await ZennArticleService("idea").get_articles()

    assert len(articles) == 1
    assert articles[0] == Article(
        title="Idea記事A", url="https://zenn.dev/user/articles/1"
    )


@respx.mock
async def test_filters_out_other_types():
    """指定した article_type 以外は除外される"""
    respx.get(ZENN_API_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "articles": [
                    _make_item(article_type="scraps", liked_count=200),
                    _make_item(article_type="book", liked_count=200),
                ]
            },
        )
    )

    articles = await ZennArticleService("tech").get_articles()

    assert articles == []


@respx.mock
async def test_filters_out_low_liked_count():
    """liked_count=49 は除外、50 は含まれる（境界値）"""
    respx.get(ZENN_API_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "articles": [
                    _make_item(title="境界未満", liked_count=49),
                    _make_item(title="境界ちょうど", liked_count=50),
                ]
            },
        )
    )

    articles = await ZennArticleService("tech").get_articles()

    assert len(articles) == 1
    assert articles[0].title == "境界ちょうど"


@respx.mock
async def test_empty_response():
    """API応答が空 → 空リスト返却"""
    respx.get(ZENN_API_URL).mock(
        return_value=httpx.Response(200, json={"articles": []})
    )

    articles = await ZennArticleService("tech").get_articles()

    assert articles == []


@respx.mock
async def test_http_error_raises():
    """API 500 エラー → httpx.HTTPStatusError が発生"""
    respx.get(ZENN_API_URL).mock(return_value=httpx.Response(500))

    import pytest

    with pytest.raises(httpx.HTTPStatusError):
        await ZennArticleService("tech").get_articles()
