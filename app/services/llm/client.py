import requests
from .config import LLMConfig

class OpenRouterClient:

    def __init__(self):
        self.base_url = LLMConfig.BASE_URL
        self.api_key = LLMConfig.API_KEY

    def chat_completion(self, payload: dict):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=60
        )

        response.raise_for_status()
        return response.json()