import requests
from .config import LLMConfig

class OpenRouterClient:

    def __init__(self):
        self.base_url = LLMConfig.BASE_URL
        self.api_key = LLMConfig.API_KEY

    def chat_completion(self, payload: dict):
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY is missing")
    
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "LinkLian"
        }
    
        response = requests.post(
            self.base_url,
            headers=headers,
            json=payload,
            timeout=60
        )
    
        response.raise_for_status()
        return response.json()