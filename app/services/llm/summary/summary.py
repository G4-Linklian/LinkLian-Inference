import base64
import time
from typing import Any
from app.services.llm.client import OpenRouterClient
from app.services.llm.config import LLMConfig, LLMSummaryEachPageConfig, LLMSummaryAllPageConfig
from app.services.llm.prompt_templates import LLMPromptTemplates
from app.services.llm.response_format import LLMResponseFormatConfig
from app.core.image import pil_image_to_base64
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

def summarize_each_page(
    image,
    page,
):
    try:
        base64_image = pil_image_to_base64(image)

        payload = {
            "model": LLMSummaryEachPageConfig.DEFAULT_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": LLMPromptTemplates.summary_each_page(page)},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": LLMSummaryEachPageConfig.DEFAULT_MAX_TOKENS,
            "temperature": LLMSummaryEachPageConfig.DEFAULT_TEMPERATURE,
            "response_format": LLMResponseFormatConfig.SUMMARY_EACH_PAGE
        }

        return _call_with_retry(payload, label="summarize_each_page")

    except Exception as e:
        logger.error(
            "summarize_each_page failed",
            "LLMSummary",
            {"page": page, "error": str(e)},
        )
        raise

def summarize_all_page(
    text,
    title,
    content,
):
    try:
        payload = {
            "model": LLMSummaryAllPageConfig.DEFAULT_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": LLMPromptTemplates.summary_all_page_prompt(title, content)
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "max_tokens": LLMSummaryAllPageConfig.DEFAULT_MAX_TOKENS,
            "temperature": LLMSummaryAllPageConfig.DEFAULT_TEMPERATURE,
            "response_format": LLMResponseFormatConfig.SUMMARY_ALL_PAGE
        }

        return _call_with_retry(payload, label="summarize_all_page")

    except Exception as e:
        logger.error(
            "summarize_all_page failed",
            "LLMSummary",
            {"title": title, "error": str(e)},
        )
        raise


