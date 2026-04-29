import time
from typing import Any
from app.services.llm.client import OpenRouterClient
from app.services.llm.config import LLMRewriteConfig
from app.services.llm.prompt_templates import LLMPromptTemplates
from app.services.llm.response_format import LLMResponseFormatConfig
from app.core.logger import AppLogger

client = OpenRouterClient()
logger = AppLogger()


def _call_with_retry(payload: dict, *, label: str, max_attempts: int = 3) -> str:
    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            result = client.chat_completion(payload)
            content = result.get("choices", [{}])[0].get("message", {}).get("content")
            if content:
                return content
            raise ValueError(f"{label} returned empty content")
        except Exception as e:
            last_error = e
            logger.warn(
                f"{label} failed, attempt {attempt}/{max_attempts}",
                "LLMSummary",
                {"error": str(e)},
            )
            if attempt < max_attempts:
                time.sleep(1.5 * attempt)

    raise last_error or RuntimeError(f"{label} failed after {max_attempts} attempts")

def rewrite(
    text: str,
    summary_context: str,
    chat_history: list,
):

    user_content = f"""
DOCUMENT SUMMARY CONTEXT:
{summary_context}

CHAT HISTORY:
{chat_history}

USER TEXT:
{text}
"""

    payload = {
        "model": LLMRewriteConfig.DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": LLMPromptTemplates.rewrite_qa_prompt()
            },
            {
                "role": "user",
                "content": user_content
            }
        ],
        "temperature": LLMRewriteConfig.DEFAULT_TEMPERATURE,
        "max_tokens": LLMRewriteConfig.DEFAULT_MAX_TOKENS,
        "response_format": LLMResponseFormatConfig.REWRITE_RESPONSE_FORMAT
    }

    return _call_with_retry(payload, label="rewrite")