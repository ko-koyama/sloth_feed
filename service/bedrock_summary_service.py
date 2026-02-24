import logging
import os

import boto3

from interface.i_summary_service import ISummaryService
from model.summary_result import SummaryResult

logger = logging.getLogger(__name__)

DEFAULT_MODEL_ID = "global.anthropic.claude-sonnet-4-6"

_SYSTEM_PROMPT = """\
あなたは技術記事を要約するアシスタントです。
与えられた記事を読み、output_summaryツールを使って結果を返してください。"""

_TOOL_DEF = {
    "toolSpec": {
        "name": "output_summary",
        "description": "記事の要約と用語解説を出力する",
        "inputSchema": {
            "json": {
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "記事の要点を最大5つ。各項目は50文字以内の短い1文にすること。",
                    },
                    "glossary": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "term": {"type": "string"},
                                "explanation": {"type": "string"},
                            },
                            "required": ["term", "explanation"],
                        },
                        "description": "専門用語の解説。専門用語がない場合は省略。",
                    },
                },
                "required": ["summary"],
            }
        },
    }
}


class BedrockSummaryService(ISummaryService):
    def __init__(self, client=None) -> None:
        self._client = client or boto3.client(
            "bedrock-runtime", region_name="ap-northeast-1"
        )
        self._model_id = os.environ.get("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)

    async def summarize(self, title: str, body: str) -> SummaryResult:
        user_message = f"# {title}\n\n{body}"
        response = self._client.converse(
            modelId=self._model_id,
            system=[{"text": _SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_message}]}],
            toolConfig={
                "tools": [_TOOL_DEF],
                "toolChoice": {"tool": {"name": "output_summary"}},
            },
        )
        tool_input = self._extract_tool_input(response)
        return SummaryResult(
            summary=tool_input["summary"],
            glossary=tool_input.get("glossary"),
        )

    def _extract_tool_input(self, response: dict) -> dict:
        content = response["output"]["message"]["content"]
        for block in content:
            if block.get("toolUse", {}).get("name") == "output_summary":
                return block["toolUse"]["input"]
        raise ValueError("output_summary tool use block not found in response")
