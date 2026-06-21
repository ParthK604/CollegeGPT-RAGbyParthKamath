from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    clerk_id: str
    name: str
    email: str
    provider: str
    created_at: datetime

