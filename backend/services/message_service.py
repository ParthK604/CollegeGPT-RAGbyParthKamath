from typing import List

from db.mongo import db
from models.message import Message


async def create_message(
    message_data: Message
) -> str:

    collection = db["messages"]

    message_dict = (
        message_data.model_dump()
    )

    try:

        result = await collection.insert_one(
            message_dict
        )

        return str(
            result.inserted_id
        )

    except Exception as e:

        print(
            f"Error creating message: {e}"
        )

        raise


async def get_messages_by_chat(
    chat_id: str
) -> List[dict]:

    collection = db["messages"]

    try:

        cursor = collection.find(
            {"chat_id": chat_id}
        )

        messages = await cursor.to_list(
            length=1000
        )

        for message in messages:

            message["_id"] = str(
                message["_id"]
            )

        return messages

    except Exception as e:

        print(
            f"Error fetching messages: {e}"
        )

        raise


async def delete_messages_by_chat(
    chat_id: str
) -> bool:

    collection = db["messages"]

    try:

        result = await collection.delete_many(
            {"chat_id": chat_id}
        )

        return (
            result.deleted_count > 0
        )

    except Exception as e:

        print(
            f"Error deleting messages: {e}"
        )

        raise