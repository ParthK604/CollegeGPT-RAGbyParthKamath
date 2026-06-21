from pinecone import Pinecone
from pathlib import Path
from dotenv import load_dotenv
from typing import List, Any
import numpy as np
import uuid
import os

env_path = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(env_path)

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = "collegegpt"


class PineconeService:

    def __init__(self):

        self.pc = Pinecone(
            api_key=PINECONE_API_KEY
        )

        self.index = self.pc.Index(
            PINECONE_INDEX_NAME
        )

    def insert_into_vector_db(
        self,
        chunks: List[Any],
        embeddings: np.ndarray
    ):

        if len(chunks) != len(embeddings):
            raise ValueError(
                "Chunks and embeddings count mismatch"
            )

        vectors = []

        for i, (doc, embedding) in enumerate(
            zip(chunks, embeddings)
        ):

            vector_id = (
                f"chunk_"
                f"{uuid.uuid4().hex[:8]}_"
                f"{i}"
            )

            metadata = {
                "text": doc.page_content,
                "page": doc.metadata.get("page", 0),
                "source": doc.metadata.get(
                    "source",
                    ""
                )
            }

            vectors.append(
                {
                    "id": vector_id,
                    "values": embedding.tolist(),
                    "metadata": metadata
                }
            )

        self.index.upsert(
            vectors=vectors
        )

        return len(vectors)