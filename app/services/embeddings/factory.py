from app.core.config import get_settings
from app.services.embeddings.base import BaseEmbeddingClient
from app.services.embeddings.mock import MockEmbeddingClient
from app.services.embeddings.openai_compatible import OpenAICompatibleEmbeddingClient


def get_embedding_client() -> BaseEmbeddingClient:
    settings = get_settings()

    if settings.embedding_provider == "mock":
        return MockEmbeddingClient(dimension=settings.embedding_dimension)

    if settings.embedding_provider == "openai_compatible":
        return OpenAICompatibleEmbeddingClient()

    raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")