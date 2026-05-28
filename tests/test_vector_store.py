from app.schemas.chunk import TextChunk
from app.services.embeddings.mock import MockEmbeddingClient
from app.services.vector_store import VectorStoreService


# 向量库向量化和存储测试
def test_add_chunks_to_vector_store():
    chunks = [
        TextChunk(
            chunk_id="test_doc_chunk_0",
            document_id="test_doc",
            chunk_index=0,
            content="This is a test chunk.",
            content_length=len("This is a test chunk."),
            metadata={
                "document_id": "test_doc",
                "source": "test",
            },
        )
    ]

    embedding_client = MockEmbeddingClient(dimension=384)
    embeddings = embedding_client.embed_texts([chunk.content for chunk in chunks])

    vector_store = VectorStoreService()
    count = vector_store.add_chunks(chunks, embeddings) # return the number of chunks added

    assert count == 1


# 向量库检索测试
def test_similarity_search_from_vector_store():
    chunks = [
        TextChunk(
            chunk_id="search_test_doc_chunk_0",
            document_id="search_test_doc",
            chunk_index=0,
            content="Enterprise RAG supports document upload and vector search.",
            content_length=len("Enterprise RAG supports document upload and vector search."),
            metadata={
                "document_id": "search_test_doc",
                "source": "search_test.txt",
            },
        )
    ]

    embedding_client = MockEmbeddingClient(dimension=384)
    embeddings = embedding_client.embed_texts([chunk.content for chunk in chunks])

    vector_store = VectorStoreService()
    vector_store.add_chunks(chunks, embeddings)

    query_embedding = embedding_client.embed_texts(
        ["Enterprise RAG supports document upload and vector search."]
    )[0]

    results = vector_store.similarity_search(
        query_embedding=query_embedding,
        top_k=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == "search_test_doc_chunk_0"
    assert "document upload" in results[0].content
    assert results[0].metadata["source"] == "search_test.txt"