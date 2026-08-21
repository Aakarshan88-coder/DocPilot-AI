from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.dependencies.auth import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.models.chat import ChatMessage, ChatSession
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
    chat_id: int | None = None


class ChatSessionRequest(BaseModel):
    document_id: int | None = None


def serialize_chat(chat):
    return {
        "id": chat.id,
        "title": chat.title,
        "document_id": chat.document_id,
        "created_at": chat.created_at,
        "updated_at": chat.updated_at,
        "messages": [
            {
                "role": message.role,
                "text": message.text,
                "sources": message.sources or [],
            }
            for message in chat.messages
        ],
    }


def get_owned_chat(db, chat_id, user_id):
    return db.query(ChatSession).filter(
        ChatSession.id == chat_id,
        ChatSession.user_id == user_id,
    ).first()


@router.get("/sessions")
def list_chat_sessions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chats = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
    ).order_by(
        ChatSession.updated_at.desc(),
        ChatSession.created_at.desc(),
    ).all()

    return [serialize_chat(chat) for chat in chats]


@router.post("/sessions")
def create_chat_session(
    chat_request: ChatSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = ChatSession(
        title="New conversation",
        user_id=current_user.id,
        document_id=chat_request.document_id,
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return serialize_chat(chat)


@router.delete("/sessions/{chat_id}")
def delete_chat_session(
    chat_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    chat = get_owned_chat(db, chat_id, current_user.id)

    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully", "chat_id": chat_id}


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

    chat = None

    if chat_request.chat_id is not None:
        chat = get_owned_chat(
            db=db,
            chat_id=chat_request.chat_id,
            user_id=current_user.id,
        )

        if not chat:
            raise HTTPException(status_code=404, detail="Chat not found")
    else:
        chat = ChatSession(
            title=chat_request.question[:255],
            user_id=current_user.id,
            document_id=chat_request.document_id,
        )
        db.add(chat)
        db.flush()

    if chat.title == "New conversation":
        chat.title = chat_request.question[:255]

    chat.document_id = chat_request.document_id


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
        top_k=5
    )

    if not results:
        answer = "I could not find this information in the uploaded document."

        chat.messages.extend([
            ChatMessage(role="user", text=chat_request.question, sources=[]),
            ChatMessage(role="assistant", text=answer, sources=[]),
        ])
        db.commit()

        return {
            "question": chat_request.question,
            "document_id": chat_request.document_id,
            "answer": answer,
            "sources": [],
            "chat_id": chat.id,
        }


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

    chat.messages.extend([
        ChatMessage(role="user", text=chat_request.question, sources=[]),
        ChatMessage(role="assistant", text=answer, sources=results),
    ])
    db.commit()


    return {
        "question": chat_request.question,
        "document_id": chat_request.document_id,
        "answer": answer,
        "sources": results,
        "chat_id": chat.id,
    }