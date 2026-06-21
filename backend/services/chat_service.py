from typing import List, Optional
from bson import ObjectId
from models.chat import Chat
from db.mongo import db


async def create_chat(chat_data: Chat) -> str:

    collection = db["chats"]

    chat_dict = chat_data.model_dump()

    try:
        result = await collection.insert_one(
            chat_dict
        )

        return str(result.inserted_id)

    except Exception as e:
        print(
            f"Error creating chat: {e}"
        )
        raise


async def get_user_chats(
    user_id: str
) -> List[dict]:

    collection = db["chats"]

    try:

        cursor = collection.find(
            {"user_id": user_id}
        )

        chats = await cursor.to_list(
            length=1000
        )

        for chat in chats:
            chat["_id"] = str(
                chat["_id"]
            )

        return chats

    except Exception as e:
        print(
            f"Error fetching chats: {e}"
        )
        raise


async def get_chat_by_id(
    chat_id: str
) -> Optional[dict]:

    collection = db["chats"]

    try:

        chat = await collection.find_one(
        {"_id": ObjectId(chat_id)}
        )

        if chat:
            chat["_id"] = str(
                chat["_id"]
            )

        return chat

    except Exception as e:
        print(
            f"Error fetching chat: {e}"
        )
        raise


async def delete_chat_by_id(
    chat_id: str
) -> bool:

    collection = db["chats"]

    try:

        result = await collection.delete_one(
        {"_id": ObjectId(chat_id)}
        )

        return result.deleted_count > 0

    except Exception as e:
        print(
            f"Error deleting chat: {e}"
        )
        raise