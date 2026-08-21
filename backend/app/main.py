from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database.database import Base, engine
from app.models.user import User
from app.models.document import Document
from app.models.chat import ChatSession, ChatMessage

from app.routers.auth import router as auth_router
from app.routers.document import router as document_router
from app.routers.chat import router as chat_router


# =========================
# Database
# =========================

Base.metadata.create_all(
    bind=engine
)


# =========================
# Rate Limiter
# =========================

limiter = Limiter(
    key_func=get_remote_address
)


# =========================
# FastAPI App
# =========================

app = FastAPI()


# Register rate limiter
app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)


# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================
# Routers
# =========================

app.include_router(
    auth_router
)

app.include_router(
    document_router,
    prefix="/documents"
)

app.include_router(
    chat_router,
    prefix="/chat"
)