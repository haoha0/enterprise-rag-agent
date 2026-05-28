from openai import OpenAI

from app.core.config import get_settings
from app.services.embeddings.base import BaseEmbeddingClient


class OpenAICompatibleEmbeddingClient(BaseEmbeddingClient):
    def __init__(self) -> None:
        self.settings = get_settings()

        if not self.settings.embedding_api_key:
            raise ValueError(
                "EMBEDDING_API_KEY is required when EMBEDDING_PROVIDER=openai_compatible."
            )

        client_kwargs = {
            "api_key": self.settings.embedding_api_key,
        }

        if self.settings.embedding_base_url:
            client_kwargs["base_url"] = self.settings.embedding_base_url

        self.client = OpenAI(**client_kwargs)

        # SiliconFlow 当前单次 embedding batch 上限较小，这里保守设为 64
        self.batch_size = 64

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        all_embeddings: list[list[float]] = []

        for start in range(0, len(texts), self.batch_size):
            batch_texts = texts[start : start + self.batch_size]

            response = self.client.embeddings.create(
                model=self.settings.embedding_model,
                input=batch_texts,
            )

            batch_embeddings = [item.embedding for item in response.data]
            all_embeddings.extend(batch_embeddings)

        return all_embeddings