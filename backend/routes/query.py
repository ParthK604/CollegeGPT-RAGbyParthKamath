from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime, UTC

from services.retrieval import RAGRetrieval
from services.llm import LLMService
from services.embeddings import EmbeddingService
from services.pinecone_services import PineconeService
from services.message_service import create_message

from models.message import Message

routerq = APIRouter()


class QueryReq(BaseModel):
    chat_id: str
    question: str


@routerq.post("/query")
async def gen_for_query(req: QueryReq):

    embedder = EmbeddingService()
    pinecone = PineconeService()

    retriever = RAGRetrieval(
        pinecone,
        embedder
    )

    llm_service = LLMService()

    question = req.question
    chat_id = req.chat_id

    user_msg = Message(
        chat_id=chat_id,
        role="user",
        content=question,
        created_at=datetime.now(UTC)
    )

    user_msg_id = await create_message(
        user_msg
    )

    llm_reply = llm_service.generate_answer(
        question,
        retriever
    )

    assistant_msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=llm_reply,
        created_at=datetime.now(UTC)
    )

    assistant_msg_id = await create_message(
        assistant_msg
    )

    return {
        "user_message_id": user_msg_id,
        "assistant_message_id": assistant_msg_id,
        "answer": llm_reply
    }