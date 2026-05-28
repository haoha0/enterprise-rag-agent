from pydantic import BaseModel, Field


class RetrieveRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question or search query")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of chunks to retrieve")


class RetrievedChunk(BaseModel):
    chunk_id: str
    content: str
    score: float | None = None
    metadata: dict


class RetrieveResponse(BaseModel):
    query: str
    top_k: int
    results: list[RetrievedChunk]

class AnswerRequest(BaseModel):
    query: str = Field(..., min_length=1, description="User question")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of chunks to retrieve")


class AnswerResponse(BaseModel):
    query: str
    answer: str
    sources: list[RetrievedChunk]