from pydantic import BaseModel


class TextChunk(BaseModel):
    chunk_id: str
    document_id: str
    chunk_index: int
    content: str
    content_length: int
    metadata: dict