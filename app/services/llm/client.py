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
    
        original_model = payload.get("model")
        models_to_try: list[str] = []

        if isinstance(original_model, str) and original_model:
            models_to_try.append(original_model)

        for fallback_model in LLMConfig.MODEL_FALLBACKS:
            if fallback_model not in models_to_try:
                models_to_try.append(fallback_model)

        if not models_to_try:
            raise ValueError("No OpenRouter model configured")

        last_error: requests.HTTPError | None = None
        for model in models_to_try:
            request_payload = dict(payload)
            request_payload["model"] = model

            response = requests.post(
                self.base_url,
                headers=headers,
                json=request_payload,
                timeout=60,
            )

            if response.ok:
                return response.json()

            error_detail = response.text
            try:
                body = response.json()
                # OpenRouter errors are typically under body["error"]["message"].
                message = body.get("error", {}).get("message")
                if message:
                    error_detail = message
            except ValueError:
                pass

            error = requests.HTTPError(
                f"OpenRouter request failed ({response.status_code}) with model '{model}': {error_detail}",
                response=response,
            )

            is_region_blocked = (
                response.status_code == 403
                and "not available in your region" in error_detail.lower()
            )

            if is_region_blocked:
                last_error = error
                continue

            raise error

        raise last_error or RuntimeError("OpenRouter request failed for all configured models")