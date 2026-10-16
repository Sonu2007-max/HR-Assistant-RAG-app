# System Design Document: Student HR & Health Insurance RAG Application

## 1. High-Level Architecture
The application follows a standard modular Retrieval-Augmented Generation (RAG) pattern, split into two main phases:
1. **Offline Ingestion & Embedding Pipeline (`ingest.py`):** Reads raw HR and insurance documents, breaks them into clean text chunks, calls Gemini Embedding API (`text-embedding-004` or equivalent), and stores vectors in ChromaDB.
2. **Online Query & Generation Service (`app.py`):** A Streamlit/Chainlit web app that accepts user questions, embeds the query, retrieves top-$K$ matching chunks from ChromaDB, constructs an augmented prompt, and queries the Gemini LLM (`gemini-2.5-flash`).

---

## 2. Component Diagram & Data Flow

```
[ Raw Knowledge Base ] (HR Policy & Insurance Docs)
         │
         ▼
[ Ingestion Script (ingest.py) ] ──► Semantic Chunking
         │
         ▼
[ Gemini Embedding API ] ──► Vector Generation
         │
         ▼
[ ChromaDB (Local Vector Store) ] ◄── (ANN Retrieval)
         ▲
         │ (Top-K Chunks)
[ Streamlit / Chainlit Web UI ] ◄── User Query ("What is my maternity leave limit?")
         │
         ▼
[ Gemini LLM API (Answer Synthesis + Citations) ]
```

---

## 3. Technology Stack & Justification
*   **Language:** Python 3.10+ (Industry standard for AI/ML).
*   **LLM & Embeddings:** Gemini API (`google-genai` SDK) — provides state-of-the-art reasoning and native multimodal embedding support.
*   **Vector Database:** ChromaDB — lightweight, runs locally with zero complex server setup, perfect for student projects.
*   **UI Framework:** Streamlit or Chainlit — enables rapid interactive web app development with minimal Python code.
