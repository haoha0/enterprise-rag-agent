from app.services.llms.mock import MockLLMClient


def test_mock_llm_generate():
    client = MockLLMClient()

    answer = client.generate("Tell me about RAG.")

    assert isinstance(answer, str)
    assert len(answer) > 0
    assert "mock RAG answer" in answer