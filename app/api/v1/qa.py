from fastapi import APIRouter

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
def answer(request: AnswerRequest) -> AnswerResponse:
    service = QAService()
    return service.answer(request)