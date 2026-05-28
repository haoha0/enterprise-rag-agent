import hashlib
import random

from app.services.embeddings.base import BaseEmbeddingClient


# mock embedding，后续替换为真实的Embedding API，eg. OpenAIEmbeddingClient, QwenEmbeddingClient
class MockEmbeddingClient(BaseEmbeddingClient):
    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        seed = int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32)
        rng = random.Random(seed)

        return [rng.uniform(-1.0, 1.0) for _ in range(self.dimension)]