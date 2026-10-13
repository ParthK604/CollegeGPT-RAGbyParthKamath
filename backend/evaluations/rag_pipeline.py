# backend/evaluations/rag_pipeline.py
import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ---- Load Config ----
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

# Verify core credentials exist early to prevent silent runtime failure
required_env = ["GROQ_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
for var in required_env:
    if not os.getenv(var):
        raise KeyError(f"Missing required environment variable: {var}")

INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

# ---- 1. Initialize Embeddings & Vector Store Retrievability ----
# Note: Ensure the model matches what you used to build your index chunks!
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'}
)

vector_store = PineconeVectorStore(
    index_name=INDEX_NAME,
    embedding=embeddings,
    pinecone_api_key=os.environ["PINECONE_API_KEY"]
)

# Configure the retriever to pull only the most useful passages during evaluation.
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# ---- 2. Initialize the Generation Model Setup ----
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0.0, # 0.0 temperature ensures objective, grounded generation behavior
    max_tokens=512
)

# ---- 3. Define the Prompt Structure ----
RAG_PROMPT_TEMPLATE = """You are an assistant for question-answering tasks at CollegeGPT. \
Use the following pieces of retrieved context to answer the question. If you don't know the answer, \
say that you don't know. Keep the answer concise and strictly factual to the context.

Context:
{context}

Question: 
{question}

Answer:"""

prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

# ---- 4. Helper to format documents safely ----
def format_docs(docs):
    """Combines text contents of multiple documents into a single contextual block."""
    return "\n\n".join(doc.page_content for doc in docs)

# ---- 5. Build LCEL (LC expression language) chain for answer generation only (context passed in) ----
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

generation_chain = prompt | llm | StrOutputParser()

# ---- 6. Target Entry Point for LangSmith Platform Evaluations ----
def evaluate_college_gpt(inputs: dict) -> dict:
    question = inputs["question"]

    # Retrieve once — reuse the same docs for both the context sent to
    # the LLM and the context returned for eval scoring, so faithfulness
    # scoring is checking the actual grounding, not a second, possibly
    # different retrieval.
    retrieved_docs = retriever.invoke(question)
    formatted_context = format_docs(retrieved_docs)

    generated_answer = generation_chain.invoke(
        {"context": formatted_context, "question": question}
    )

    return {
        "answer": generated_answer,
        "contexts": [doc.page_content for doc in retrieved_docs],
    }
