from sqlalchemy.orm import Session

from app.repositories.qa_record_repository import QARecordRepository
from app.schemas.qa import (
    AnswerRequest,
    AnswerResponse,
    RetrieveRequest,
    RetrieveResponse,
)
# from app.schemas.qa import RetrieveRequest, RetrieveResponse
from app.services.embeddings.factory import get_embedding_client
from app.services.vector_store import VectorStoreService

from app.services.llms.factory import get_llm_client
from app.services.prompt_builder import PromptBuilder


class QAService:
    def __init__(self, db: Session | None = None) -> None:
        self.embedding_client = get_embedding_client()
        self.vector_store = VectorStoreService()
        self.llm_client = get_llm_client()
        self.prompt_builder = PromptBuilder()
        self.qa_record_repository = QARecordRepository(db) if db else None

    def retrieve(self, request: RetrieveRequest) -> RetrieveResponse:
        query_embedding = self.embedding_client.embed_texts([request.query])[0]

        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            top_k=request.top_k,
        )

        return RetrieveResponse(
            query=request.query,
            top_k=request.top_k,
            results=results,
        )
    
    def answer(self, request: AnswerRequest) -> AnswerResponse:
        retrieve_response = self.retrieve(
            RetrieveRequest(
                query=request.query,
                top_k=request.top_k,
            )
        )

        prompt = self.prompt_builder.build_rag_prompt(
            query=request.query,
            retrieved_chunks=retrieve_response.results,
        )

        answer = self.llm_client.generate(prompt)

        if self.qa_record_repository:
            self.qa_record_repository.create_record(
                question=request.query,
                answer=answer,
                top_k=request.top_k,
                retrieved_chunk_ids=[
                    chunk.chunk_id for chunk in retrieve_response.results
                ],
            )

        return AnswerResponse(
            query=request.query,
            answer=answer,
            sources=retrieve_response.results,
        )
