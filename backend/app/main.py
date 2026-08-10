from fastapi import FastAPI

from app.database.database import Base, engine
from app.models.user import User
from app.models.document import Document

from app.routers.auth import router as auth_router
from app.routers.document import router as document_router


Base.metadata.create_all(bind=engine)

app = FastAPI()


app.include_router(auth_router)
app.include_router(document_router, prefix="/documents")