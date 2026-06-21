from services.message_service import (
    create_message,
    get_messages_by_chat,
    delete_messages_by_chat
)

from models.message import Message
from fastapi import APIRouter
from datetime import datetime, UTC

routerm = APIRouter()


@routerm.get("/message/{chat_id}")
async def get_messages(chat_id: str):

    messages = await get_messages_by_chat(
        chat_id
    )

    return messages


@routerm.delete("/message/{chat_id}")
async def delete_messages(chat_id: str):

    result = await delete_messages_by_chat(
        chat_id
    )

    return {
        "deleted": result
    }