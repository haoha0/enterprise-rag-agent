from fastapi import APIRouter, File, HTTPException, UploadFile, status, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.document import DocumentUploadResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post(
    "/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> DocumentUploadResponse:
    service = DocumentService(db=db)

    try:
        return service.save_uploaded_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc