from pydantic import BaseModel
from datetime import datetime


class Document(BaseModel):
    user_id: str="defaultuser"
    filename: str
    vector_count: int
    created_at: datetime

