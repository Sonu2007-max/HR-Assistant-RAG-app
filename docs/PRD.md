# Product Requirement Document (PRD): Enterprise HR & Health Insurance RAG Assistant

## 1. Project Overview & Objective
The goal of this project is to build an intelligent, grounded **HR & Health Insurance Assistant (RAG App)** that helps employees instantly and accurately answer queries regarding company leave policies, medical insurance coverage, network hospitals, and disease procedures. 

Students will build this application using **Python, Gemini API (for embeddings and text generation), ChromaDB (as the local vector database), and Streamlit or Chainlit (for the chat interface)**.

---

## 2. Target Users & Use Cases
*   **Target Users:** Company employees seeking quick, accurate answers about HR policies and health benefits.
*   **Key Use Cases:**
    *   *Leave Policy Queries:* "How many earned leaves do I get per year? Can I encash them?"
    *   *Health Insurance Coverage:* "Is dental surgery covered under the corporate health plan?"
    *   *Hospital Network Lookups:* "Which network hospitals are nearest for emergency hospitalization?"
    *   *Claim Procedures:* "What documents do I need to submit for maternity claim reimbursement?"

---

## 3. Core Functional Requirements
1. **Document Ingestion & Chunking:** Ingest Markdown/Text files containing HR policies and health insurance guidelines, split them into semantic chunks, and generate vector embeddings.
2. **Vector Storage (ChromaDB):** Store embeddings locally in ChromaDB for fast approximate nearest neighbor (ANN) retrieval.
3. **Retrieval-Augmented Generation (RAG):** When a user asks a question, perform a similarity search in ChromaDB, retrieve the top relevant context chunks, and pass them along with the query to the Gemini API.
4. **Interactive Web UI:** Provide a clean, conversational chat interface using **Streamlit** or **Chainlit** where employees can type questions and receive grounded answers complete with source citations.
5. **Copilot Integration:** Students will use GitHub Copilot / AI assistants to scaffold code, write docstrings, and debug errors.

---

## 🚀 4. Starter Guide & Implementation Roadmap for Mentees (Soma Nath & Krishna)

To build this Enterprise HR & Health Insurance RAG Assistant from scratch, follow this step-by-step roadmap:

### Step 1: Environment & Project Setup
1. Create a clean project folder structure:
   ```text
   student-hr-rag-app/
   ├── data/                 # Place raw HR & insurance policy text/markdown files here
   ├── db/                   # Local ChromaDB persistent storage
   ├── src/
   │   ├── ingest.py         # Document loader, chunking & vector store builder
   │   ├── rag_engine.py     # Retrieval & Gemini LLM chain logic
   │   └── app.py            # Streamlit / Chainlit chat UI
   ├── requirements.txt      # Python dependencies
   └── README.md
   ```
2. Install required Python packages (`pip install -r requirements.txt`):
   ```text
   streamlit
   chromadb
   langchain
   langchain-community
   langchain-google-genai
   python-dotenv
   ```
3. Set up your Gemini API Key in a `.env` file:
   ```env
   GOOGLE_API_KEY="your-gemini-api-key-here"
   ```

### Step 2: Build the Ingestion Pipeline (`src/ingest.py`)
* Read sample HR policy documents from the `data/` folder.
* Use `RecursiveCharacterTextSplitter` (chunk_size=500, chunk_overlap=50).
* Generate embeddings using `GoogleGenerativeAIEmbeddings` (`models/embedding-001`).
* Save and persist embeddings locally using `Chroma`.

### Step 3: Implement the RAG Engine (`src/rag_engine.py`)
* Load the persistent Chroma vector store.
* Create a retriever with top-$K = 3$ similarity search.
* Configure `ChatGoogleGenerativeAI` (model=`gemini-1.5-flash`).
* Construct a strict prompt template that forces the LLM to answer *only* from the retrieved context.

### Step 4: Create the Interactive Web App (`src/app.py`)
* Build a user-friendly chat interface using **Streamlit** (`st.chat_input`, `st.chat_message`).
* Maintain chat history so employees can ask follow-up questions.
* Display source document citations alongside the generated answer.

### Step 5: Test, Refine & Build in Public!
* Test edge cases (e.g., asking about policies not in the documents to verify hallucination prevention).
* Document your progress, push code to GitHub, and share learnings on LinkedIn/Slack as part of the Gurukul Build-in-Public initiative.

