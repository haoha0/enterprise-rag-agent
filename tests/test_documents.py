from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_upload_txt_document():
    files = {
        "file": (
            "test.txt",
            b"This is a test document for RAG.",
            "text/plain",
        )
    }

    response = client.post("/api/v1/documents/upload", files=files)

    assert response.status_code == 201

    data = response.json()

    assert data["original_filename"] == "test.txt"
    assert data["file_extension"] == ".txt"
    assert data["status"] == "uploaded"
    assert data["file_size"] > 0
    assert data["parse_status"] == "parsed"
    assert data["text_length"] > 0
    assert "test document" in data["text_preview"]

    # 加入分片测试断言
    assert data["chunk_status"] == "chunked"
    assert data["chunk_count"] > 0

    # 加入向量存储测试断言
    assert data["vector_status"] == "stored"
    assert data["vector_count"] > 0


def test_upload_markdown_document():
    files = {
        "file": (
            "readme.md",
            b"# Project Title\n\nThis is a markdown document.",
            "text/markdown",
        )
    }

    response = client.post("/api/v1/documents/upload", files=files)

    assert response.status_code == 201

    data = response.json()

    assert data["original_filename"] == "readme.md"
    assert data["file_extension"] == ".md"
    assert data["parse_status"] == "parsed"
    assert "markdown document" in data["text_preview"]

    assert data["chunk_status"] == "chunked"
    assert data["chunk_count"] > 0

    assert data["vector_status"] == "stored"
    assert data["vector_count"] > 0


def test_upload_unsupported_file_type():
    files = {
        "file": (
            "test.exe",
            b"fake exe content",
            "application/octet-stream",
        )
    }

    response = client.post("/api/v1/documents/upload", files=files)

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]