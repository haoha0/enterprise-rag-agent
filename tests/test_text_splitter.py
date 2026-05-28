import pytest

from app.services.text_splitter import TextSplitter


def test_split_text_into_chunks():
    splitter = TextSplitter(chunk_size=10, chunk_overlap=2)

    chunks = splitter.split_text(
        text="abcdefghijklmnopqrstuvwxyz",
        document_id="doc_1",
        metadata={"source": "test.txt"},
    )

    assert len(chunks) == 4

    assert chunks[0].content == "abcdefghij"
    assert chunks[1].content == "ijklmnopqr"
    assert chunks[2].content == "qrstuvwxyz"
    assert chunks[3].content == "yz"

    assert chunks[0].chunk_id == "doc_1_chunk_0"
    assert chunks[0].metadata["source"] == "test.txt"
    assert chunks[0].metadata["start_char"] == 0
    assert chunks[0].metadata["end_char"] == 10


def test_split_empty_text():
    splitter = TextSplitter(chunk_size=10, chunk_overlap=2)

    chunks = splitter.split_text(
        text="   ",
        document_id="doc_1",
    )

    assert chunks == []


def test_invalid_chunk_config():
    with pytest.raises(ValueError):
        TextSplitter(chunk_size=10, chunk_overlap=10)

    with pytest.raises(ValueError):
        TextSplitter(chunk_size=0, chunk_overlap=0)

    with pytest.raises(ValueError):
        TextSplitter(chunk_size=10, chunk_overlap=-1)