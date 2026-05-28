from openai import OpenAI

from app.core.config import get_settings
from app.services.llms.base import BaseLLMClient


class OpenAICompatibleLLMClient(BaseLLMClient):
    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.llm_api_key:
            raise ValueError("LLM_API_KEY is required when LLM_PROVIDER=openai_compatible.")

        client_kwargs = {
            "api_key": self.settings.llm_api_key,
        }

        if self.settings.llm_base_url:
            client_kwargs["base_url"] = self.settings.llm_base_url

        self.client = OpenAI(**client_kwargs)

    def generate(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.llm_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are a concise and factual enterprise knowledge base assistant.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=self.settings.llm_temperature,
        )

        content = response.choices[0].message.content

        if not content:
            return ""

        return content.strip()