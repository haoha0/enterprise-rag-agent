from app.schemas.qa import RetrievedChunk
from app.services.prompt_builder import PromptBuilder


def test_build_rag_prompt():
    builder = PromptBuilder()

    chunks = [
        RetrievedChunk(
            chunk_id="doc_1_chunk_0",
            content="Enterprise RAG supports document upload and vector search.",
            score=0.9,
            metadata={
                "original_filename": "test.txt",
            },
        )
    ]

    prompt = builder.build_rag_prompt(
        query="What does the system support?",
        retrieved_chunks=chunks,
    )

    assert "Enterprise RAG supports document upload" in prompt
    assert "What does the system support?" in prompt
    assert "test.txt" in prompt
    assert "Answer:" in prompt