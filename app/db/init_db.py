from app.db.base import Base
from app.db.session import engine

# Import models here so SQLAlchemy can register them.
from app.models.chunk import ChunkModel  # noqa: F401
from app.models.document import DocumentModel  # noqa: F401
from app.models.qa_record import QARecordModel  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)