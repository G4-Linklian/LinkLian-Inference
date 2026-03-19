import os


def _csv_env(name: str, default: str) -> list[str]:
    value = os.getenv(name, default)
    return [item.strip() for item in value.split(",") if item.strip()]

class LLMConfig:
    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    API_KEY = os.getenv("OPENROUTER_API_KEY")
    SITE_URL = os.getenv("OPENROUTER_SITE_URL", "http://localhost")
    APP_TITLE = os.getenv("OPENROUTER_APP_TITLE", "LinkLian")
    DEFAULT_MODEL = os.getenv("OPENROUTER_DEFAULT_MODEL", "openai/gpt-4o-mini")
    MODEL_FALLBACKS = _csv_env(
        "OPENROUTER_MODEL_FALLBACKS",
        "openai/gpt-4o-mini,meta-llama/llama-3.1-8b-instruct",
    )
    DEFAULT_MAX_TOKENS = 200
    DEFAULT_TEMPERATURE = 0.0
    
class LLMSummaryEachPageConfig:
    DEFAULT_MODEL = os.getenv("OPENROUTER_SUMMARY_EACH_MODEL", LLMConfig.DEFAULT_MODEL)
    DEFAULT_MAX_TOKENS = 700
    DEFAULT_TEMPERATURE = 0.3
    
class LLMSummaryAllPageConfig:
    DEFAULT_MODEL = os.getenv("OPENROUTER_SUMMARY_ALL_MODEL", LLMConfig.DEFAULT_MODEL)
    DEFAULT_MAX_TOKENS = 3000
    DEFAULT_TEMPERATURE = 0.3
    
class LLMQuizGenerationConfig:
    DEFAULT_MODEL = os.getenv("OPENROUTER_QUIZ_MODEL", LLMConfig.DEFAULT_MODEL)
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TEMPERATURE = 0.3
    
class LLMRewriteConfig:
    DEFAULT_MODEL = os.getenv("OPENROUTER_REWRITE_MODEL", LLMConfig.DEFAULT_MODEL)
    DEFAULT_MAX_TOKENS = 300
    DEFAULT_TEMPERATURE = 0.1
    
class LLMQAConfig:
    DEFAULT_MODEL = os.getenv("OPENROUTER_QA_MODEL", LLMConfig.DEFAULT_MODEL)
    DEFAULT_MAX_TOKENS = 1000
    DEFAULT_TEMPERATURE = 0.8