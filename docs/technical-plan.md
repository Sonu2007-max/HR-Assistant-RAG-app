# Technical Solution Plan & Implementation Guide

## 1. Directory Structure
```
student-hr-rag-app/
├── data/
│   └── raw/
│       ├── hr_policy.md
│       └── health_insurance_policy.md
├── docs/
│   ├── PRD.md
│   ├── system-design.md
│   └── technical-plan.md
├── src/
│   ├── ingest.py
│   └── rag_engine.py
├── app.py
├── requirements.txt
└── .env.example
```

---

## 2. Step-by-Step Implementation Plan

### Step 1: Dependencies Setup (`requirements.txt`)
Students will install the required packages:
```text
google-genai>=0.1.0
chromadb>=0.4.22
streamlit>=1.31.0
python-dotenv>=1.0.0
markdown>=3.5.0
```

### Step 2: Knowledge Base Creation (`data/raw/`)
We will provide two comprehensive Markdown documents covering HR policies and Health Insurance details.

### Step 3: Ingestion & Vectorization (`src/ingest.py`)
- Read markdown files.
- Split text into paragraphs/sections.
- Initialize ChromaDB client.
- Generate embeddings via Gemini API and store them in ChromaDB.

### Step 4: RAG Engine & LLM Querying (`src/rag_engine.py`)
- Accept user query string.
- Query ChromaDB for top-3 relevant chunks.
- Format prompt with retrieved context and user query.
- Call Gemini model (`gemini-2.5-flash`) to generate grounded response.

### Step 5: Web Application (`app.py`)
- Build a chat UI using Streamlit (`st.chat_input` and `st.chat_message`).
- Connect UI actions to `rag_engine.py`.
- Display response along with source document citations.
