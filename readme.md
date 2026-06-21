collegegpt/
│
├── frontend/                        # Next.js (JS)
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/[[...sign-in]]/
│   │   │   │   └── page.jsx
│   │   │   └── sign-up/[[...sign-up]]/
│   │   │       └── page.jsx
│   │   ├── dashboard/
│   │   │   └── page.jsx             # doc list + upload
│   │   ├── chat/
│   │   │   └── [docId]/
│   │   │       └── page.jsx         # chat UI per doc
│   │   ├── layout.jsx               # ClerkProvider wraps here
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
│   │   └── api.js                   # all axios calls to FastAPI
│   │
│   ├── middleware.js                 # Clerk route protection
│   ├── next.config.js
│   └── .env.local                   # NEXT_PUBLIC_ vars + FastAPI URL
│
├── backend/                         # FastAPI (Python)
│   ├── main.py                      # app entry, CORS config
│   ├── routes/
│   │   ├── upload.py                # POST /upload
│   │   ├── query.py                 # POST /query
│   │   └── documents.py             # GET /documents, DELETE /document
│   ├── services/
│   │   ├── pdf_processor.py         # PyMuPDF + LangChain splitting
│   │   ├── embeddings.py            # all-MiniLM + Pinecone upsert
│   │   ├── llm.py                   # Groq chain
│   │   
│   ├── db/
│   │   └── mongo.py                 # MongoDB connection via Motor
│   ├── models/
│   │   ├── document.py              # Pydantic schemas
│   │   └── chat.py
│   ├── config.py                    # all env vars via pydantic
│   ├── requirements.txt
│   └── .env                         # Python side keys
│
└── README.md