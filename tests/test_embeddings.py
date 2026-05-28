from app.services.embeddings.mock import MockEmbeddingClient


def test_mock_embedding_dimension():
    client = MockEmbeddingClient(dimension=384)

    embeddings = client.embed_texts(["hello world"])    # 这里传入的是List[str]

    assert len(embeddings) == 1
    assert len(embeddings[0]) == 384


def test_mock_embedding_is_stable():
    client = MockEmbeddingClient(dimension=384)

    embedding_1 = client.embed_texts(["same text"])[0]
    embedding_2 = client.embed_texts(["same text"])[0]

    assert embedding_1 == embedding_2