"""
Document Ingestion & Vector Storage Pipeline
Supports multi-format parsing (PDF, Markdown, Text), chunking,
embedding generation via Google Gemini API, and ChromaDB persistence.
"""

import os
import io
import re
from pathlib import Path
from dotenv import load_dotenv
import chromadb
from google import genai
import pypdf

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY or API_KEY == "your_gemini_api_key_here":
    raise ValueError("GEMINI_API_KEY not found or invalid in .env file. Please add your Gemini API Key.")

# Initialize Gemini Client
client = genai.Client(api_key=API_KEY)

# Define directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw"
DB_DIR = BASE_DIR / "db" / "chroma_store"
COLLECTION_NAME = "hr_insurance_policy"


def get_chroma_collection():
    """Returns or creates the ChromaDB collection."""
    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "HR and Health Insurance Policies"}
    )


def extract_text_from_bytes(file_bytes: bytes, filename: str) -> str:
    """Extract plain text from uploaded file bytes (supports .pdf, .md, .txt)."""
    ext = Path(filename).suffix.lower()
    if ext == ".pdf":
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        pages_text = []
        for i, page in enumerate(reader.pages):
            txt = page.extract_text()
            if txt:
                pages_text.append(f"\n--- Page {i+1} ---\n" + txt)
        return "\n".join(pages_text).strip()
    elif ext in [".md", ".txt"]:
        return file_bytes.decode("utf-8", errors="replace").strip()
    else:
        raise ValueError(f"Unsupported file format '{ext}'. Please upload .pdf, .md, or .txt files.")


def infer_category(filename: str) -> str:
    """Infer document category based on filename."""
    lower_name = filename.lower()
    if any(k in lower_name for k in ["insurance", "health", "mediclaim", "hospital", "coverage", "claim"]):
        return "Health Insurance"
    elif any(k in lower_name for k in ["hr", "leave", "holiday", "attendance", "maternity", "resignation", "code"]):
        return "HR & Leaves"
    return "General Policies"


def chunk_document(text: str, filename: str, category: str = None, chunk_size: int = 500, overlap: int = 60) -> list[dict]:
    """
    Split text into section/paragraph-aware chunks with rich metadata.
    """
    if category is None:
        category = infer_category(filename)

    # Split by markdown headers if present, else by double newlines
    if re.search(r'\n#{1,3}\s', text):
        sections = re.split(r'\n(?=#{1,3}\s)', text)
    else:
        sections = text.split("\n\n")

    chunks = []
    chunk_index = 0

    for sec in sections:
        sec = sec.strip()
        if not sec:
            continue
        
        # If section is small enough, keep as single chunk
        if len(sec) <= chunk_size:
            chunk_index += 1
            chunks.append({
                "id": f"{filename}_{chunk_index}",
                "text": sec,
                "metadata": {
                    "source": filename,
                    "category": category,
                    "chunk_id": chunk_index
                }
            })
        else:
            # Split larger sections into sliding window chunks
            start = 0
            while start < len(sec):
                end = min(start + chunk_size, len(sec))
                chunk_slice = sec[start:end].strip()
                if chunk_slice:
                    chunk_index += 1
                    chunks.append({
                        "id": f"{filename}_{chunk_index}",
                        "text": chunk_slice,
                        "metadata": {
                            "source": filename,
                            "category": category,
                            "chunk_id": chunk_index
                        }
                    })
                if end == len(sec):
                    break
                start = end - overlap

    return chunks


def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings using Gemini gemini-embedding-001.
    """
    embeddings = []
    batch_size = 20
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        response = client.models.embed_content(
            model="gemini-embedding-001",
            contents=batch
        )
        for emb in response.embeddings:
            embeddings.append(emb.values)
    return embeddings


def add_document_to_store(filename: str, file_bytes: bytes, category: str = None) -> int:
    """
    Extracts text, chunks, embeds, and upserts a document into ChromaDB.
    Also saves a copy in data/raw/ for persistence.
    """
    text = extract_text_from_bytes(file_bytes, filename)
    if not text:
        raise ValueError(f"No extractable text found in '{filename}'.")

    # Persist the file in data/raw/
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    save_path = DATA_DIR / filename
    with open(save_path, "wb") as f:
        f.write(file_bytes)

    if category is None:
        category = infer_category(filename)

    chunks = chunk_document(text, filename, category=category)
    if not chunks:
        return 0

    texts = [c["text"] for c in chunks]
    ids = [c["id"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    embeddings = generate_embeddings(texts)
    collection = get_chroma_collection()

    # Upsert chunks
    collection.upsert(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    return len(chunks)


def delete_document_from_store(filename: str) -> int:
    """Removes all chunks of a specific file from ChromaDB."""
    collection = get_chroma_collection()
    existing = collection.get(where={"source": filename})
    if existing and existing.get("ids"):
        collection.delete(ids=existing["ids"])
        # Also remove file from data/raw if present
        saved_file = DATA_DIR / filename
        if saved_file.exists():
            saved_file.unlink()
        return len(existing["ids"])
    return 0


def get_indexed_stats() -> dict:
    """Returns statistics about indexed documents in ChromaDB."""
    try:
        collection = get_chroma_collection()
        data = collection.get(include=["metadatas"])
        total_chunks = len(data.get("ids", []))
        metadatas = data.get("metadatas", []) or []

        sources = {}
        for m in metadatas:
            src = m.get("source", "Unknown")
            cat = m.get("category", "General Policies")
            if src not in sources:
                sources[src] = {"count": 0, "category": cat}
            sources[src]["count"] += 1

        return {
            "total_chunks": total_chunks,
            "documents": sources,
            "categories": sorted(list({m.get("category", "General Policies") for m in metadatas}))
        }
    except Exception:
        return {"total_chunks": 0, "documents": {}, "categories": []}


def ingest_documents():
    """
    Main function to read documents from data/raw/, generate embeddings, and persist in ChromaDB.
    """
    print(f"Loading documents from: {DATA_DIR}")
    doc_files = list(DATA_DIR.glob("*.md")) + list(DATA_DIR.glob("*.txt")) + list(DATA_DIR.glob("*.pdf"))

    if not doc_files:
        print("No documents found in data/raw/!")
        return

    chroma_client = chromadb.PersistentClient(path=str(DB_DIR))
    try:
        chroma_client.delete_collection(name=COLLECTION_NAME)
    except Exception:
        pass

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "HR and Health Insurance Policies"}
    )

    all_chunks = []
    for file_path in doc_files:
        print(f"Processing: {file_path.name}")
        with open(file_path, "rb") as f:
            content_bytes = f.read()
        try:
            text = extract_text_from_bytes(content_bytes, file_path.name)
            chunks = chunk_document(text, file_path.name)
            all_chunks.extend(chunks)
        except Exception as e:
            print(f"Skipping {file_path.name}: {e}")

    print(f"Total chunks created: {len(all_chunks)}")
    if not all_chunks:
        return

    texts = [c["text"] for c in all_chunks]
    ids = [c["id"] for c in all_chunks]
    metadatas = [c["metadata"] for c in all_chunks]

    print("Generating embeddings via Gemini API...")
    embeddings = generate_embeddings(texts)

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas
    )

    print(f"Successfully ingested {len(all_chunks)} policy chunks into ChromaDB collection '{COLLECTION_NAME}'!")


if __name__ == "__main__":
    ingest_documents()

