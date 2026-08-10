from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import os
from app.services.chunking_service import create_chunks
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.document_service import create_document,get_user_documents
from app.services.pdf_service import extract_text_from_pdf
router = APIRouter()

UPLOAD_DIR = "uploads"

os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    document = create_document(
        db=db,
        filename=file.filename,
        file_path=file_path,
        user_id=current_user.id
    )

    text = extract_text_from_pdf(file_path)
    chunks = create_chunks(text)
    return {
        "message": "Document uploaded successfully",
        "document_id": document.id,
        "filename": document.filename,
        "text": text,
        "chunks": chunks
    }