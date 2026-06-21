from fastapi import APIRouter
from datetime import datetime, UTC

from services.chat_service import (
    create_chat,
    delete_chat_by_id,
    get_chat_by_id,
    get_user_chats
)

from models.chat import Chat

routerc = APIRouter()

@routerc.get("/chats")
async def get_all_chats(user_id: str):

    chats = await get_user_chats(user_id)

    return chats


@routerc.get("/chat/{chat_id}")
async def get_chat_by_chat_id(chat_id: str):

    chat = await get_chat_by_id(chat_id)

    return chat


@routerc.delete("/chat/{chat_id}")
async def delete_chat_by_chat_id(chat_id: str):

    deleted = await delete_chat_by_id(chat_id)

    return {
        "deleted": deleted
    }