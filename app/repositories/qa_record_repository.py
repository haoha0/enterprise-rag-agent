from sqlalchemy.orm import Session

from app.models.qa_record import QARecordModel


class QARecordRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_record(
        self,
        *,
        question: str,
        answer: str,
        top_k: int,
        retrieved_chunk_ids: list[str],
    ) -> QARecordModel:
        record = QARecordModel(
            question=question,
            answer=answer,
            top_k=top_k,
            retrieved_chunk_ids=retrieved_chunk_ids,
        )

        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)

        return record