from pydantic import BaseModel
from datetime import datetime


class Message(BaseModel):
    chat_id: str
    role: str
    content: str
    created_at: datetime