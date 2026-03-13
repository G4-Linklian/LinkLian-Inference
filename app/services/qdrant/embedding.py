import os
import time
import requests


OPENROUTER_EMBEDDINGS_URL = "https://openrouter.ai/api/v1/embeddings"


def embed_text(text: str, max_attempts: int = 3) -> list[float]:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is required")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "model": "openai/text-embedding-3-small",
        "input": text,
    }

    last_error: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            res = requests.post(
                OPENROUTER_EMBEDDINGS_URL,
                headers=headers,
                json=data,
                timeout=60,
            )
            res.raise_for_status()
            return res.json()["data"][0]["embedding"]
        except Exception as e:
            last_error = e
            if attempt < max_attempts:
                time.sleep(1.5 * attempt)

    raise last_error or RuntimeError("Embedding request failed after retries")
