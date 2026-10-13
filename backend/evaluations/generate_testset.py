# backend/evalutations/generate_testset.py
import os
import json
import time
from pathlib import Path

from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv

# ---- Config ----
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
OUTPUT_PATH = Path(__file__).resolve().parent / "eval_set.json"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
MAX_CHUNKS = 40          
SLEEP_BETWEEN_CALLS = 1  

# Load the environment variables from the parent directory
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

if "GROQ_API_REFERENCE" not in os.environ:
    raise KeyError("GROQ_API_REFERENCE key not found in environment or .env file.")

GROQ_API_KEY = os.environ["GROQ_API_REFERENCE"]

SYSTEM_PROMPT = """You are generating evaluation data for a RAG system that answers \
questions from college course PDFs. Given a passage of text, write exactly ONE \
question that can be fully answered using only that passage, and its correct answer.

Respond with ONLY valid JSON in this exact format, no other text:
{"question": "...", "answer": "..."}

Rules:
- The question must be answerable using only the given passage.
- The answer must be concise and directly grounded in the passage.
- Do not ask about page numbers, document formatting, or metadata.
- Do not include any text outside the JSON object.
"""


def load_pdfs_from_dir(directory: Path) -> list[Document]:
    docs = []
    pdf_paths = sorted(directory.glob("*.pdf"))
    for pdf_path in pdf_paths:
        try:
            reader = PdfReader(str(pdf_path))
            for page_num, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                if not text.strip():
                    continue
                docs.append(
                    Document(
                        page_content=text,
                        metadata={"source": pdf_path.name, "page": page_num},
                    )
                )
        except Exception as e:
            print(f"Skipping unreadable file {pdf_path.name}: {e}")
    return docs


def chunk_documents(documents: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def generate_qa_pair(llm: ChatGroq, chunk_text: str) -> dict | None:
    try:
        response = llm.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=f"Passage:\n\n{chunk_text}"),
            ]
        )
        raw = response.content.strip()
        
        # Robust cleanup of markdown blocks if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:].strip()
            raw = raw.strip("` \n")
            
        parsed = json.loads(raw)
        if "question" in parsed and "answer" in parsed:
            return parsed
    except Exception:
        pass  # Gracefully drop unparseable generations
    return None


def main():
    print(f"Loading PDFs from {UPLOADS_DIR} ...")
    documents = load_pdfs_from_dir(UPLOADS_DIR)
    print(f"Loaded {len(documents)} pages")

    chunks = chunk_documents(documents)
    print(f"Split into {len(chunks)} chunks")

    if len(chunks) > MAX_CHUNKS:
        chunks = chunks[:MAX_CHUNKS]
        print(f"Capped to first {MAX_CHUNKS} chunks for this run")

    llm = ChatGroq(
        model="openai/gpt-oss-20b",
        api_key=GROQ_API_KEY,
        temperature=0.3,
    )

    records = []
    skipped = 0
    for i, chunk in enumerate(chunks):
        print(f"[{i + 1}/{len(chunks)}] generating QA pair ...")
        qa = generate_qa_pair(llm, chunk.page_content)
        if qa is None:
            skipped += 1
            time.sleep(SLEEP_BETWEEN_CALLS)
            continue
        records.append(
            {
                "question": qa["question"],
                "ground_truth": qa["answer"],
                "context": chunk.page_content,
                "source": chunk.metadata.get("source"),
                "page": chunk.metadata.get("page"),
            }
        )
        time.sleep(SLEEP_BETWEEN_CALLS)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(records)} QA pairs to {OUTPUT_PATH} ({skipped} chunks skipped)")


if __name__ == "__main__":
    main()
