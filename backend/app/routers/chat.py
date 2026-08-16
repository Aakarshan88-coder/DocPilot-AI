from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.services.document_service import get_user_document
from app.services.embedding_service import create_embedding
from app.services.vector_store_service import search_similar
from app.services.gemini_service import generate_answer


router = APIRouter()


# =========================
# Rate Limiter
# =========================

limiter = Limiter(
    key_func=get_remote_address
)


class ChatRequest(BaseModel):
    question: str
    document_id: int


@router.post("/ask")
@limiter.limit("10/minute")
def ask_question(
    request: Request,
    chat_request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # =========================
    # 1. Verify document ownership
    # =========================

    document = get_user_document(
        db=db,
        document_id=chat_request.document_id,
        user_id=current_user.id
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )


    # =========================
    # 2. Create question embedding
    # =========================

    question_embedding = create_embedding(
        chat_request.question
    )


    # =========================
    # 3. Search document chunks
    # =========================

    results = search_similar(
        embedding=question_embedding,
        user_id=current_user.id,
        document_id=chat_request.document_id,
        top_k=3
    )


    # =========================
    # 4. Create context
    # =========================

    context = "\n\n".join(
        item["chunk"]
        for item in results
    )


    # =========================
    # 5. Generate AI answer
    # =========================

    answer = generate_answer(
        question=chat_request.question,
        context=context
    )


    return {
        "question": chat_request.question,
        "document_id": chat_request.document_id,
        "answer": answer,
        "sources": results
    }