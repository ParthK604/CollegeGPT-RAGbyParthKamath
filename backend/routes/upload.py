from fastapi import APIRouter, File, Form, UploadFile, HTTPException
from pathlib import Path
from datetime import datetime, UTC

from services.chat_service import create_chat
from services.embeddings import EmbeddingService
from services.document_service import create_document
from services.pdf_processor import process_pdf, Chunks
from services.pinecone_services import PineconeService

from models.document import Document
from models.chat import Chat

router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    user_id: str = Form("default")
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided"
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files allowed"
        )

    filename = Path(file.filename).name
    file_path = UPLOAD_DIR / filename

    with open(file_path, "wb") as f:
        f.write(await file.read())

    documents = process_pdf(str(file_path))

    chunker = Chunks()
    chunks = chunker.chunk_docs(documents)

    embedder = EmbeddingService()
    embeddings = embedder.embed_chunks(chunks)

    pinecone_service = PineconeService()
    pinecone_service.insert_into_vector_db(
        chunks,
        embeddings
    )

    doc = Document(
        user_id=user_id,
        filename=filename,
        vector_count=len(chunks),
        created_at=datetime.now(UTC)
    )

    document_id = await create_document(doc)

    chat = Chat(
        user_id=user_id,
        document_id=document_id,
        title=filename,
        created_at=datetime.now(UTC)
    )

    chat_id = await create_chat(chat)

    return {
        "document_id": document_id,
        "chat_id": chat_id,
        "filename": filename,
        "pages": len(documents),
        "chunks": len(chunks)
    }