# CollegeGPT — AI-Powered PDF Study Assistant

Upload your lecture notes, textbooks, or any PDF and chat with them intelligently. CollegeGPT uses a **Retrieval-Augmented Generation (RAG)** pipeline to answer questions grounded strictly in your uploaded documents — no hallucination, no guessing.

---

## What It Does

```
User uploads DBMS_notes.pdf
        ↓
User asks: "Explain ACID properties with examples"
        ↓
System retrieves the most relevant chunks from the PDF
        ↓
Groq LLM answers using only retrieved content
        ↓
Chat history saved — conversation continues naturally
```

Each user has private, isolated documents. Your notes are never mixed with another user's.

---

## Architecture

```
[Next.js Frontend]
      |
      | axios REST calls
      |
[FastAPI Backend]
      |
      ├── POST /upload
      │     ↓
      │   PyMuPDF extracts text
      │     ↓
      │   LangChain splits into chunks
      │     ↓
      │   all-MiniLM-L6-v2 embeds chunks
      │     ↓
      │   Pinecone stores vectors
      │   namespace: {clerk_id}_{doc_id}
      │     ↓
      │   MongoDB stores document metadata
      │
      └── POST /query
            ↓
          Query embedded (same model)
            ↓
          Pinecone cosine similarity search
          Top 4 chunks retrieved
            ↓
          Groq llama3 generates answer
          context-restricted prompt
            ↓
          Response returned to frontend
          Chat saved to MongoDB
```

---

## Key Design Decisions

**Why FastAPI over Node/Express for the backend?**
The AI/ML ecosystem lives in Python — HuggingFace, LangChain, sentence-transformers. FastAPI gives async performance comparable to Express while keeping full access to the Python AI stack.

**Why Pinecone namespaces for user isolation?**
Each document's vectors are stored under a namespace combining the user's Clerk ID and document ID. A query for user A only searches that namespace — user B's documents are never touched.

**Why context-restricted prompting?**
The LLM is explicitly instructed to answer only from retrieved chunks. If the answer is not in the document, it says so. This eliminates hallucination entirely for document-based queries.

**Why separate frontend and backend?**
Next.js API routes run Node.js — no access to sentence-transformers or LangChain. FastAPI as a separate Python service handles all AI logic. Next.js handles UI and calls FastAPI like any external REST API.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React |
| Backend | FastAPI (Python) |
| LLM | Groq (qwen/qwen3.6-27b) |
| Embeddings | Sentence Transformers (all-MiniLM-L6-v2) |
| Vector Store | Pinecone |
| PDF Processing | PyMuPDF + LangChain |
| Database | MongoDB (Motor async driver) |
| Auth | Clerk |
| API calls | axios |

---

## Project Structure

```
collegegpt/
│
├── frontend/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/[[...sign-in]]/
│   │   │   │   └── page.jsx
│   │   │   └── sign-up/[[...sign-up]]/
│   │   │       └── page.jsx
│   │   ├── dashboard/
│   │   │   └── page.jsx         # document list + upload
│   │   ├── chat/
│   │   │   └── [docId]/
│   │   │       └── page.jsx     # chat UI per document
│   │   ├── layout.jsx           # ClerkProvider wraps here
│   │   └── globals.css
│   │
│   ├── components/
│   │   ├── UploadButton.jsx
│   │   ├── ChatWindow.jsx
│   │   ├── MessageBubble.jsx
│   │   ├── DocCard.jsx
│   │   └── Navbar.jsx
│   │
│   ├── lib/
│   │   └── api.js               # all axios calls to FastAPI
│   │
│   ├── middleware.js             # Clerk route protection
│   ├── next.config.js
│   └── .env.local
│
├── backend/
│   ├── main.py                  # FastAPI entry, CORS
│   ├── routes/
│   │   ├── upload.py            # POST /upload
│   │   ├── query.py             # POST /query
│   │   └── documents.py        # GET /documents, DELETE /document
│   ├── services/
│   │   ├── pdf_processor.py    # PyMuPDF + LangChain splitting
│   │   ├── embeddings.py       # all-MiniLM embeddings + Pinecone upsert
│   │   └── llm.py              # Groq LangChain chain
│   ├── db/
│   │   └── mongo.py            # MongoDB connection via Motor
│   ├── models/
│   │   ├── document.py         # Pydantic schemas
│   │   └── chat.py
│   ├── config.py               # env vars via Pydantic settings
│   ├── requirements.txt
│   └── .env
│
└── README.md
```

---

## Setup and Running

### Prerequisites
- Python 3.10+
- Node.js v18+
- Accounts: Groq, Pinecone, MongoDB Atlas, Clerk

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd collegegpt
```

### 2. Backend setup

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env` —

```
GROQ_API_KEY=
PINECONE_API_KEY=
PINECONE_INDEX_NAME=
MONGODB_URI=
CLERK_SECRET_KEY=
```

Run backend —

```bash
uvicorn main:app --reload --port 8000
```

### 3. Frontend setup

```bash
cd frontend
npm install
```

Create `frontend/.env.local` —

```
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=
CLERK_SECRET_KEY=
NEXT_PUBLIC_FASTAPI_URL=http://localhost:8000
```

Run frontend —

```bash
npm run dev
```

Open `http://localhost:3000`

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload` | Upload PDF, chunk, embed, store in Pinecone |
| POST | `/query` | Query document, retrieve chunks, generate answer |
| GET | `/documents` | List user's uploaded documents |
| DELETE | `/document/{id}` | Remove document and its Pinecone vectors |

---

## Document Ingestion Pipeline

```
User uploads PDF
        ↓
PyMuPDF extracts raw text page by page
        ↓
LangChain RecursiveCharacterTextSplitter
500 token chunks — 50 token overlap
Splits at paragraph/sentence boundaries first
        ↓
all-MiniLM-L6-v2 generates 384-dim embeddings
        ↓
Pinecone upserts vectors
namespace: {clerk_id}_{doc_id}
metadata: {filename, page_number, chunk_index}
        ↓
MongoDB stores document record
{clerkId, docId, filename, uploadedAt, pineconeNamespace}
```

---

## Query Pipeline

```
User sends question
        ↓
Same embedding model encodes query → 384-dim vector
        ↓
Pinecone cosine similarity search
namespace filtered to user's document only
Top 4 chunks returned
        ↓
Chunks + query sent to Groq llama3
with context-restricted system prompt —
"Answer only from the context below.
 If the answer is not in the context, say so."
        ↓
Answer returned to frontend
        ↓
MongoDB saves message to chat history
{clerkId, docId, role, content, timestamp}
```

---

## MongoDB Collections

```js
// documents
{
  clerkId: "user_abc",
  docId: "doc_xyz",
  filename: "DBMS_notes.pdf",
  pineconeNamespace: "user_abc_doc_xyz",
  uploadedAt: Date
}

// chats
{
  clerkId: "user_abc",
  docId: "doc_xyz",
  messages: [
    { role: "user", content: "...", timestamp: Date },
    { role: "assistant", content: "...", timestamp: Date }
  ]
}
```

---

Built by **Parth Kamath** — Third Year Computer Engineering, TSEC Mumbai
GitHub: github.com/ParthK604
