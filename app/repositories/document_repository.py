from sqlalchemy.orm import Session

from app.models.document import DocumentModel


class DocumentRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(
        self,
        *,  # 要求传参必须写明参数名，如 file_size=1024
        document_id: str,
        original_filename: str,
        saved_filename: str,
        file_path: str,
        file_extension: str,
        content_type: str | None,
        file_size: int,
        text_length: int,
        chunk_count: int,
        vector_count: int,
        status: str = "indexed",
    ) -> DocumentModel:
        document = DocumentModel(
            document_id=document_id,
            original_filename=original_filename,
            saved_filename=saved_filename,
            file_path=file_path,
            file_extension=file_extension,
            content_type=content_type,
            file_size=file_size,
            text_length=text_length,
            chunk_count=chunk_count,
            vector_count=vector_count,
            status=status,
        )

        # SQLAlchemy写入
        self.db.add(document)   # 将新组装好的 Python 对象放入 Session（暂存区）
        self.db.commit()        # 提交事务，真正将这条 INSERT 语句发给 PostgreSQL 数据库
        self.db.refresh(document)   # 从数据库中重新加载对象，确保获取到最新的数据

        return document