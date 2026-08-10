from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: int
    filename: str
    file_path: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True