from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    original_filename: str
    saved_filename: str
    file_path: str
    file_extension: str
    content_type: str | None
    file_size: int
    status: str

    parse_status: str
    text_length: int
    text_preview: str

    chunk_status: str
    chunk_count: int

    # embedding
    vector_status: str
    vector_count: int