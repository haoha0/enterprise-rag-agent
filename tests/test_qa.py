from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_retrieve_api():
    upload_files = {
        "file": (
            "qa_test.txt",
            b"Enterprise RAG system supports document upload, parsing, chunking, embedding and vector search.",
            "text/plain",
        )
    }

    upload_response = client.post(
        "/api/v1/documents/upload",
        files=upload_files,
    )

    assert upload_response.status_code == 201

    retrieve_response = client.post(
        "/api/v1/qa/retrieve",
        json={
            "query": "What does the enterprise RAG system support?",
            "top_k": 3,
        },
    )

    assert retrieve_response.status_code == 200

    data = retrieve_response.json()

    assert data["query"] == "What does the enterprise RAG system support?"
    assert data["top_k"] == 3
    assert isinstance(data["results"], list)
    assert len(data["results"]) >= 1

    first_result = data["results"][0]

    assert "chunk_id" in first_result
    assert "content" in first_result
    assert "metadata" in first_result

def test_answer_api():
    upload_files = {
        "file": (
            "answer_test.txt",
            b"Enterprise RAG supports document upload, parsing, chunking, embedding, vector search and LLM answer generation.",
            "text/plain",
        )
    }

    upload_response = client.post(
        "/api/v1/documents/upload",
        files=upload_files,
    )

    assert upload_response.status_code == 201

    answer_response = client.post(
        "/api/v1/qa/answer",
        json={
            "query": "What does Enterprise RAG support?",
            "top_k": 3,
        },
    )

    assert answer_response.status_code == 200

    data = answer_response.json()

    assert data["query"] == "What does Enterprise RAG support?"
    assert "answer" in data
    assert "sources" in data
    assert isinstance(data["sources"], list)
    assert len(data["sources"]) >= 1