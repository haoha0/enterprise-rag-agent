from app.core.config import get_settings
from app.services.llms.base import BaseLLMClient
from app.services.llms.mock import MockLLMClient
from app.services.llms.openai_compatible import OpenAICompatibleLLMClient


def get_llm_client() -> BaseLLMClient:
    settings = get_settings()

    if settings.llm_provider == "mock":
        return MockLLMClient()
    
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleLLMClient()

    raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")