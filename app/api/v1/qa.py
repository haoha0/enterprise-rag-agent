from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.qa import (
    AnswerRequest,
    AnswerResponse,
    RetrieveRequest,
    RetrieveResponse,
)
# from app.schemas.qa import RetrieveRequest, RetrieveResponse
from app.services.qa_service import QAService

router = APIRouter(prefix="/qa", tags=["QA"])


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve(request: RetrieveRequest) -> RetrieveResponse:
    service = QAService()
    return service.retrieve(request)

@router.post("/answer", response_model=AnswerResponse)
# def answer(request: AnswerRequest) -> AnswerResponse:
#     service = QAService()
#     return service.answer(request)
def answer(
    request: AnswerRequest,
    db: Session = Depends(get_db),
) -> AnswerResponse:
    service = QAService(db=db)
    return service.answer(request)

# /qa/retrieve 只是检索，不保存记录
# /qa/answer 是完整问答，会保存记录