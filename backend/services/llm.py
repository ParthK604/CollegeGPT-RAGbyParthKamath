import os
from pathlib import Path
from services.pinecone_services import PineconeService
from services.embeddings import EmbeddingService
from services.retrieval import RAGRetrieval
from dotenv import load_dotenv
from langchain_groq import ChatGroq


env_path = (Path(__file__).resolve().parent.parent / ".env")

load_dotenv(env_path)


groq_api_key = os.getenv(
    "GROQ_API_KEY"
)


llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama-3.1-8b-instant",
    temperature=0.1,
    max_tokens=1000
)


class LLMService:

    def generate_answer(
        self,
        query: str,
        retriever,
        top_k: int = 4
    ):

        results = retriever.retrieve(
            query,
            top_k=top_k
        )

        context = "\n\n".join(
            doc["content"]
            for doc in results
        )

        if not context:
            return (
                "No relevant context found."
            )

        prompt = f"""
You are a helpful college assistant.

Use ONLY the provided context
to answer the question.

Context:
{context}

Question:
{query}

Answer:
"""

        response = llm.invoke(
            prompt
        )

        return response.content
    
if __name__=="__main__":
    pinecone_service = PineconeService()

    embedding_service = EmbeddingService()

    retriever = RAGRetrieval(
        pinecone_service,
        embedding_service
    )

    llm_service = LLMService()

    answer = llm_service.generate_answer(
        "What is Poisson Distribution?",
        retriever
    )

    print(answer)