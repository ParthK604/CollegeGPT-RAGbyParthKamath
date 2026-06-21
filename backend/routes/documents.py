from fastapi import APIRouter
from services.document_service import (
    get_documents_by_user
)

routerd = APIRouter()


@routerd.get("/documents")
async def get_docs(user_id: str):

    docs = await get_documents_by_user(
        user_id
    )

    return docs