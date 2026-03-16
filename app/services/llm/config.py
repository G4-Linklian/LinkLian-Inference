import os

class LLMConfig:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 200
    DEFAULT_TEMPERATURE = 0.0
    
class LLMSummaryEachPageConfig:
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 700
    DEFAULT_TEMPERATURE = 0.3
    
class LLMSummaryAllPageConfig:
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 3000
    DEFAULT_TEMPERATURE = 0.3
    
class LLMQuizGenerationConfig:
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TEMPERATURE = 0.3
    
class LLMRewriteConfig:
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 300
    DEFAULT_TEMPERATURE = 0.1
    
class LLMQAConfig:
    DEFAULT_MODEL = "google/gemini-2.5-flash-lite"
    DEFAULT_MAX_TOKENS = 1000
    DEFAULT_TEMPERATURE = 0.8