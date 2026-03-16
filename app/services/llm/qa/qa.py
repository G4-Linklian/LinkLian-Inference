import time

from app.core.logger import AppLogger
from app.services.llm.client import OpenRouterClient
from app.services.llm.config import LLMQAConfig
from app.services.llm.prompt_templates import LLMPromptTemplates
from app.services.llm.response_format import LLMResponseFormatConfig

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
                "LLMQA",
                {"error": str(e)},
            )
            if attempt < max_attempts:
                time.sleep(1.5 * attempt)

    raise last_error or RuntimeError(f"{label} failed after {max_attempts} attempts")


def qa(
    question: str,
    docs_text: str,
    chat_history: list,
) -> str:
    user_content = f"""
CHAT HISTORY:
{chat_history}

DOCUMENT CONTEXT:
{docs_text}

USER QUESTION:
{question}
"""
    
    payload = {
        "model": LLMQAConfig.DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": LLMPromptTemplates.qa_prompt(),
            },
            {
                "role": "user",
                "content": user_content,
            },
        ],
        "temperature": LLMQAConfig.DEFAULT_TEMPERATURE,
        "max_tokens": LLMQAConfig.DEFAULT_MAX_TOKENS,
        "response_format": LLMResponseFormatConfig.QA_RESPONSE_FORMAT,
    }

    return _call_with_retry(payload, label="qa")
