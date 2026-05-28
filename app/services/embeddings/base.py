from abc import ABC, abstractmethod


class BaseEmbeddingClient(ABC):
    @abstractmethod
    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError
    
# 格式规定：传入一个字符串列表，返回一个嵌套的浮点数列表（也就是向量）