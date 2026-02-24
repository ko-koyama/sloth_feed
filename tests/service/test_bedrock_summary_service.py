from unittest.mock import MagicMock

import pytest

from service.bedrock_summary_service import BedrockSummaryService
from model.summary_result import SummaryResult


def _make_converse_response(summary: list[str], glossary: list[dict] | None = None):
    tool_input = {"summary": summary}
    if glossary is not None:
        tool_input["glossary"] = glossary
    return {
        "output": {
            "message": {
                "content": [
                    {
                        "toolUse": {
                            "name": "output_summary",
                            "input": tool_input,
                        }
                    }
                ]
            }
        }
    }


def _make_service(response: dict) -> BedrockSummaryService:
    mock_client = MagicMock()
    mock_client.converse.return_value = response
    return BedrockSummaryService(client=mock_client)


async def test_summarize_returns_summary_and_glossary():
    """summary と glossary が正しく SummaryResult にマッピングされる"""
    summary = ["ポイント1", "ポイント2"]
    glossary = [{"term": "API", "explanation": "Application Programming Interface"}]
    service = _make_service(_make_converse_response(summary, glossary))

    result = await service.summarize("テスト記事", "本文テキスト")

    assert isinstance(result, SummaryResult)
    assert result.summary == summary
    assert result.glossary == glossary


async def test_summarize_returns_none_glossary_when_absent():
    """glossary が省略された場合は None になる"""
    service = _make_service(_make_converse_response(["ポイント1"]))

    result = await service.summarize("テスト記事", "本文テキスト")

    assert result.glossary is None


async def test_summarize_sends_correct_request():
    """converse に正しいモデルIDとメッセージが渡される"""
    mock_client = MagicMock()
    mock_client.converse.return_value = _make_converse_response(["要点"])
    service = BedrockSummaryService(client=mock_client)

    await service.summarize("記事タイトル", "記事本文")

    call_kwargs = mock_client.converse.call_args.kwargs
    assert "記事タイトル" in call_kwargs["messages"][0]["content"][0]["text"]
    assert "記事本文" in call_kwargs["messages"][0]["content"][0]["text"]
    tool_names = [t["toolSpec"]["name"] for t in call_kwargs["toolConfig"]["tools"]]
    assert "output_summary" in tool_names


async def test_summarize_raises_when_tool_use_not_found():
    """レスポンスに output_summary ブロックがない場合は ValueError"""
    mock_client = MagicMock()
    mock_client.converse.return_value = {
        "output": {"message": {"content": [{"text": "unexpected"}]}}
    }
    service = BedrockSummaryService(client=mock_client)

    with pytest.raises(ValueError, match="output_summary"):
        await service.summarize("タイトル", "本文")
