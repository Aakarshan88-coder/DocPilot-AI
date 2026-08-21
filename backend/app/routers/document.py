from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

import os
import uuid
import fitz

from app.services.chunking_service import create_chunks
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.services.document_service import (
    create_document,
    get_user_documents,
    delete_document
)
from app.services.pdf_service import extract_pages_from_pdf
from app.services.embedding_service import create_embedding
from app.services.vector_store_service import (
    add_embedding,
    delete_document_embeddings
)


router = APIRouter()


UPLOAD_DIR = "uploads"

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


# =========================
# Security limits
# =========================

MAX_FILE_SIZE = 10 * 1024 * 1024

MAX_PAGES = 100


@router.post("/upload")
def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    file_path = None
    document = None

    try:

        # =========================
        # 1. Check filename
        # =========================

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename"
            )

        original_filename = os.path.basename(
            file.filename
        )

        if not original_filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )


        # =========================
        # 2. Check content type
        # =========================

        if file.content_type != "application/pdf":
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are allowed"
            )


        # =========================
        # 3. Read file
        # =========================

        file_content = file.file.read()


        # =========================
        # 4. Check file size
        # =========================

        if len(file_content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File size must be less than 10 MB"
            )

        if len(file_content) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty files are not allowed"
            )


        # =========================
        # 5. Validate actual PDF
        # =========================

        if not file_content.startswith(b"%PDF"):
            raise HTTPException(
                status_code=400,
                detail="Invalid PDF file"
            )


        # =========================
        # 6. Open PDF safely
        # =========================

        try:

            pdf = fitz.open(
                stream=file_content,
                filetype="pdf"
            )

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF"
            )


        # =========================
        # 7. Reject encrypted PDF
        # =========================

        if pdf.is_encrypted:

            pdf.close()

            raise HTTPException(
                status_code=400,
                detail="Encrypted or password-protected PDFs are not allowed"
            )


        # =========================
        # 8. Check page count
        # =========================

        if len(pdf) > MAX_PAGES:

            pdf.close()

            raise HTTPException(
                status_code=400,
                detail=f"PDF cannot contain more than {MAX_PAGES} pages"
            )


        pdf.close()


        # =========================
        # 9. Generate safe filename
        # =========================

        safe_filename = f"{uuid.uuid4().hex}.pdf"

        file_path = os.path.join(
            UPLOAD_DIR,
            safe_filename
        )


        # =========================
        # 10. Save PDF
        # =========================

        with open(
            file_path,
            "wb"
        ) as buffer:

            buffer.write(file_content)


        # =========================
        # 11. Create database record
        # =========================

        document = create_document(
            db=db,
            filename=original_filename,
            file_path=file_path,
            user_id=current_user.id
        )


        # =========================
        # 12. Extract PDF text
        # =========================

        pages = extract_pages_from_pdf(
            file_path
        )

        text = "\n".join(
            page["text"]
            for page in pages
            if page["text"]
        )

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "No readable text found in this PDF. "
                    "Scanned PDFs require OCR before they can be searched."
                )
            )


        # =========================
        # 13. Create chunks
        # =========================

        chunks = []


        # =========================
        # 14. Create embeddings
        # =========================

        for page in pages:
            page_chunks = create_chunks(
                page["text"]
            )

            for chunk_index, chunk in enumerate(page_chunks):
                chunks.append(chunk)

                embedding = create_embedding(
                    chunk
                )

                add_embedding(
                    embedding=embedding,
                    document_id=document.id,
                    user_id=current_user.id,
                    chunk=chunk,
                    page_number=page["page_number"],
                    chunk_index=chunk_index
                )


        # =========================
        # 15. Response
        # =========================

        return {
            "message": "Document uploaded successfully",
            "document_id": document.id,
            "filename": document.filename,
            "text": text,
            "chunks": chunks
        }


    except HTTPException:

        raise


    except Exception as error:

        print(
            "UPLOAD ERROR:",
            error
        )

        # =========================
        # Cleanup physical file
        # =========================

        if file_path and os.path.exists(file_path):

            os.remove(file_path)


        # =========================
        # Cleanup database record
        # =========================

        if document:

            try:

                db.delete(document)
                db.commit()

            except Exception:

                db.rollback()


        raise HTTPException(
            status_code=500,
            detail="Document processing failed"
        )


@router.get("/")
def get_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    documents = get_user_documents(
        db,
        current_user.id
    )

    return documents


@router.delete("/{document_id}")
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    document = delete_document(
        db=db,
        document_id=document_id,
        user_id=current_user.id
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    # =========================
    # Delete physical PDF
    # =========================

    if os.path.exists(
        document.file_path
    ):

        os.remove(
            document.file_path
        )


    # =========================
    # Delete FAISS embeddings
    # =========================

    delete_document_embeddings(
        document_id=document_id,
        user_id=current_user.id
    )


    return {
        "message": "Document deleted successfully",
        "document_id": document_id
    }