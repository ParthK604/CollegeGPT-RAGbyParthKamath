from pydantic import BaseModel
from datetime import datetime


class Chat(BaseModel):
    user_id: str
    document_id: str
    title: str
    created_at: datetime

