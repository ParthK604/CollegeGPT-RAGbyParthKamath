from typing import List, Dict, Any

from services.pinecone_services import PineconeService
from services.embeddings import EmbeddingService

class RAGRetrieval:

    def __init__(
        self,
        pinecone_service: PineconeService,
        embedding_service: EmbeddingService
    ):
        self.pinecone_service = pinecone_service
        self.embedding_service = embedding_service

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        score_threshold: float = 0.0
    ) -> List[Dict[str, Any]]:

        query_embedding = (
            self.embedding_service
            .embed_query(query)
        )

        results = (
            self.pinecone_service.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                include_metadata=True
            )
        )

        retrieved_docs = []

        for rank, match in enumerate(
            results["matches"],
            start=1
        ):

            score = match["score"]

            if score < score_threshold:
                continue

            metadata = match.get(
                "metadata",
                {}
            )

            retrieved_docs.append(
                {
                    "id": match["id"],
                    "content": metadata.get(
                        "text",
                        ""
                    ),
                    "metadata": metadata,
                    "score": score,
                    "rank": rank
                }
            )

        return retrieved_docs

