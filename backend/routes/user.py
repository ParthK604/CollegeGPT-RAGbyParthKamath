from fastapi import APIRouter
from pydantic import BaseModel

from services.user_service import sync_user


routeru = APIRouter()


class UserSyncReq(BaseModel):
    clerk_id: str
    email: str | None = None
    name: str | None = None
    provider: str = "clerk"


@routeru.post("/user/sync")
async def user_sync(req: UserSyncReq):
    return await sync_user(req.model_dump())