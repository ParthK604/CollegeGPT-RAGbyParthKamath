from datetime import datetime, UTC

from db.mongo import db


async def sync_user(user_data: dict) -> dict:
    collection = db["users"]

    clerk_id = user_data.get("clerk_id")
    now = datetime.now(UTC)

    existing_user = await collection.find_one({"clerk_id": clerk_id})

    payload = {
        "clerk_id": clerk_id,
        "email": user_data.get("email", ""),
        "name": user_data.get("name", ""),
        "provider": user_data.get("provider", "clerk"),
        "updated_at": now,
    }

    if existing_user:
        await collection.update_one(
            {"clerk_id": clerk_id},
            {"$set": payload},
        )

        existing_user.update(payload)
        existing_user["_id"] = str(existing_user["_id"])
        return {
            "user": existing_user,
            "created": False,
        }

    payload["created_at"] = now
    result = await collection.insert_one(payload)
    payload["_id"] = str(result.inserted_id)

    return {
        "user": payload,
        "created": True,
    }