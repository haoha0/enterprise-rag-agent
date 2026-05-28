import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.schemas.document import DocumentUploadResponse
from app.services.document_parser import DocumentParser
from app.services.text_splitter import TextSplitter
from app.services.vector_store import VectorStoreService
from app.services.embeddings.factory import get_embedding_client
from app.repositories.document_repository import DocumentRepository
from app.repositories.chunk_repository import ChunkRepository

class DocumentService:
    def __init__(self, db: Session) -> None:
        self.settings = get_settings()
        self.upload_dir = Path(self.settings.upload_dir)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        self.parser = DocumentParser()
        self.text_splitter = TextSplitter(
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap
        )
        self.embedding_client = get_embedding_client()
        self.vector_store = VectorStoreService()
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)

    def validate_file_extension(self, filename: str) -> str:
        file_extension = Path(filename).suffix.lower()

        if file_extension not in self.settings.allowed_file_extensions:
            allowed = ", ".join(sorted(self.settings.allowed_file_extensions))
            raise ValueError(f"Unsupported file type: {file_extension}. Allowed: {allowed}")

        return file_extension

    def save_uploaded_file(self, file: UploadFile) -> DocumentUploadResponse:
        if not file.filename:
            raise ValueError("Filename is required.")

        file_extension = self.validate_file_extension(file.filename)

        document_id = str(uuid4())
        saved_filename = f"{document_id}{file_extension}"
        file_path = self.upload_dir / saved_filename

        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size = file_path.stat().st_size
        max_size_bytes = self.settings.max_upload_size_mb * 1024 * 1024

        if file_size > max_size_bytes:
            file_path.unlink(missing_ok=True)
            raise ValueError(
                f"File size exceeds limit: {self.settings.max_upload_size_mb}MB"
            )

        parsed_text = self.parser.parse(str(file_path))
        text_preview = parsed_text[:300]

        # text chunk
        chunks = self.text_splitter.split_text(
            text=parsed_text,
            document_id=document_id,
            metadata={
                "original_filename": file.filename,
                "saved_filename": saved_filename,
                "file_path": str(file_path),
                "file_extension": file_extension,
            },
        )

        # text embedding
        embeddings = self.embedding_client.embed_texts(
            [chunk.content for chunk in chunks]
        )

        # store
        vector_count = self.vector_store.add_chunks(
            chunks=chunks,
            embeddings=embeddings,
        )

        # create document record in database
        self.document_repository.create_document(
            document_id=document_id,
            original_filename=file.filename,
            saved_filename=saved_filename,
            file_path=str(file_path),
            file_extension=file_extension,
            content_type=file.content_type,
            file_size=file_size,
            text_length=len(parsed_text),
            chunk_count=len(chunks),
            vector_count=vector_count,
            status="indexed",
        )

        self.chunk_repository.create_chunks(chunks)

        return DocumentUploadResponse(
            document_id=document_id,
            original_filename=file.filename,
            saved_filename=saved_filename,
            file_path=str(file_path),
            file_extension=file_extension,
            content_type=file.content_type,
            file_size=file_size,
            status="uploaded",
            parse_status="parsed",
            text_length=len(parsed_text),
            text_preview=text_preview,
            chunk_status="chunked",
            chunk_count=len(chunks),
            vector_status="stored",
            vector_count=vector_count,
        )