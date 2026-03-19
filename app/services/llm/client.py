import requests
from .config import LLMConfig

class OpenRouterClient:

    def __init__(self):
        self.base_url = LLMConfig.BASE_URL
        self.api_key = LLMConfig.API_KEY

    def chat_completion(self, payload: dict):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")

        # Portainer/Stack deployments may pass an unresolved placeholder literally.
        if self.api_key.startswith("${") and self.api_key.endswith("}"):
            raise ValueError(
                "OPENROUTER_API_KEY is unresolved placeholder. Set real value in Portainer environment variables."
            )
    
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": LLMConfig.SITE_URL,
            "X-Title": LLMConfig.APP_TITLE,
        }
    
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        if not response.ok:
            error_detail = response.text
            try:
                body = response.json()
                # OpenRouter errors are typically under body["error"]["message"].
                message = body.get("error", {}).get("message")
                if message:
                    error_detail = message
            except ValueError:
                pass

            raise requests.HTTPError(
                f"OpenRouter request failed ({response.status_code}): {error_detail}",
                response=response,
            )

        return response.json()