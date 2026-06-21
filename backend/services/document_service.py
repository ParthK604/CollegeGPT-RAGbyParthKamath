from typing import List
from models.document import Document
from db.mongo import db


async def create_document(doc_data: Document) -> str:

    collection = db["documents"]

    document_dict = doc_data.model_dump()

    try:
        result = await collection.insert_one(document_dict)
        return str(result.inserted_id)

    except Exception as e:
        print(f"Error creating document: {e}")
        raise


async def get_documents_by_user(user_id: str) -> List[dict]:

    collection = db["documents"]

    try:
        cursor = collection.find(
            {"user_id": user_id}
        )

        documents = await cursor.to_list(
            length=1000
        )

        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return documents

    except Exception as e:
        print(
            f"Error fetching documents: {e}"
        )
        raise