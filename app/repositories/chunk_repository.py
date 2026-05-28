from sqlalchemy.orm import Session

from app.models.chunk import ChunkModel
from app.schemas.chunk import TextChunk


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_chunks(self, chunks: list[TextChunk]) -> list[ChunkModel]:
        chunk_models: list[ChunkModel] = []

        for chunk in chunks:
            chunk_model = ChunkModel(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                content_length=chunk.content_length,
                start_char=int(chunk.metadata.get("start_char", 0)),
                end_char=int(chunk.metadata.get("end_char", 0)),
            )
            chunk_models.append(chunk_model)

        self.db.add_all(chunk_models)
        self.db.commit()

        for chunk_model in chunk_models:
            self.db.refresh(chunk_model)

        return chunk_models