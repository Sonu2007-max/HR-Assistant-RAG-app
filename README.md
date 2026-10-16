<div align="center">

# 🏢 Enterprise HR & Health Insurance RAG Assistant
### *Grounded, Real-Time Conversational AI for Corporate Policies & Health Benefits*

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Gemini_API-3.8--Flash-8E75C2?logo=google&logoColor=white)](https://ai.google.dev/)
[![ChromaDB](https://img.shields.io/badge/Vector_DB-ChromaDB-orange?logo=databricks&logoColor=white)](https://www.trychroma.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production--Ready%20Prototype-success)](#)

<p align="center">
  <b>Instant, accurate, and hallucination-free answers to complex employee questions on leave rules, medical coverage, cashless hospitalization, waiting periods, and policy exclusions.</b>
</p>

[Key Features](#-key-features) •
[Architecture](#-system-architecture) •
[Quickstart](#-quickstart-guide) •
[Tested Queries](#-validated-test-queries) •
[Tech Stack](#-tech-stack) •
[Project Structure](#-project-structure)

---

</div>

## 📌 Problem Statement & Overview

In traditional corporate environments, employees spend hours navigating dense, multi-page PDF policy handbooks or waiting on HR ticket queues just to get simple answers about:
- *"How many sick leaves can I take before requiring a doctor's certificate?"*
- *"Is routine dental checkup covered under corporate insurance?"*
- *"What is the waiting period for pre-existing diseases?"*

**The Solution:** This project delivers an enterprise-grade **Retrieval-Augmented Generation (RAG) system** that pairs **ChromaDB's local vector indexing** with **Google Gemini 3.8-Flash** and **Streamlit**. Every generated response is strictly grounded in internal corporate documents with clear source citations and relevance scores, eliminating AI hallucinations.

---

## 🌟 Key Features

- **⚡ Real-Time Token Streaming:** Delivers token-by-token streaming via Gemini 3.8-Flash and Streamlit's `st.write_stream` for a responsive, conversational user experience.
- **📤 Dynamic Multi-Format Document Ingestion:** Upload new policy documents directly from the UI (`.pdf`, `.md`, `.txt`) using `pypdf`. Documents are automatically chunked, embedded, and added to the vector store on the fly without restarting the server.
- **📊 Knowledge Base Control Center:** Sidebar metrics display total indexed chunks, active documents, category tags, and a 1-click **Reset to Default Policies** action.
- **🎯 Domain-Specific Category Filtering:** Filter search queries across domains (*All Policies*, *HR & Leaves*, *Health Insurance*, *General Policies*) with configurable **Top-K Retrieval (2–5 chunks)**.
- **🔍 Transparent Source Citations & Relevance Scores:** Every answer features an expandable citation card detailing the source document, chunk ID, category, relevance indicator (`🟢 High`, `🟡 Medium`), and vector distance metric.
- **🛡️ Strict Anti-Hallucination Guardrails:** Low LLM temperature (0.2) paired with strict prompt constraints ensures that any out-of-scope question triggers a polite fallback redirecting to `hr@company.com`.
- **💬 Conversation Management & Markdown Export:** Reset conversations in one click or download the full Q&A transcript in clean Markdown format for HR audit trails and records.

---

## 🏗️ System Architecture

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                             DOCUMENT INGESTION                              │
│  data/raw/*.md, *.pdf, *.txt  ──►  PyPDF / Text Parser  ──► Semantic Chunker │
│                                                                    │        │
│                                                                    ▼        │
│                                              Gemini Embedding API (001)     │
│                                                                    │        │
│                                                                    ▼        │
│                                                        ChromaDB Vector Store│
└─────────────────────────────────────────────────────────────────────────────┘
                                       ▲
                                       │ Top-K Similarity Search
┌──────────────────────────────────────┼──────────────────────────────────────┐
│                               CHAT / INFERENCE                              │
│                                      │                                      │
│  [ Employee Query ] ──► [ Streamlit UI (app.py) ]                           │
│                                      │                                      │
│                                      ▼                                      │
│                     Embed Query & Retrieve Context                          │
│                                      │                                      │
│                                      ▼                                      │
│           Prompt Synthesis (Context + Query + Guardrails)                   │
│                                      │                                      │
│                                      ▼                                      │
│                     Google Gemini 3.8-Flash (Streaming)                     │
│                                      │                                      │
│                                      ▼                                      │
│             Verified Answer + Source Citations + Relevance Badges           │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component | Technology | Description |
| :--- | :--- | :--- |
| **LLM Model** | `Google Gemini 3.8-Flash` | High-speed, high-reasoning conversational generation |
| **Embedding Model** | `models/gemini-embedding-001` | Semantic text embeddings for vector retrieval |
| **Vector Database** | `ChromaDB` (Persistent) | Local on-disk vector store with Cosine / L2 distance metrics |
| **Web Interface** | `Streamlit` | Interactive web application with real-time token streaming |
| **PDF Extraction** | `PyPDF` | Memory-efficient PDF text parsing |
| **Environment & Config** | `python-dotenv` | Secure API key and runtime configuration management |

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/student-hr-rag-app.git
cd student-hr-rag-app
```

### 2. Create and Activate Virtual Environment
```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Your Gemini API Key
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key_here
```
> Get your free Gemini API key from [Google AI Studio](https://aistudio.google.com/).

### 5. Ingest Initial Policy Documents
Populate the ChromaDB vector database with the bundled HR and Health Insurance policies:
```bash
python src/ingest.py
```
*(You will see a success message showing 12 chunks indexed into `db/chroma_store/`)*

### 6. Launch the Streamlit App
```bash
streamlit run app.py
```
Open your browser at **[http://localhost:8501](http://localhost:8501)**.

---

## 🧪 Validated Test Queries

The following queries have been benchmarked against the bundled corporate policy documents:

| Test Query | Expected Response & Grounding | Relevance |
| :--- | :--- | :---: |
| **Maternity Leave** | **26 weeks of paid leave** for up to 2 surviving children; can start up to 8 weeks prior to delivery. | `🟢 High` |
| **Paternity Leave** | **2 weeks of paid leave** to be availed within 6 months of child birth/adoption. | `🟢 High` |
| **Sum Insured** | **₹5,00,000 (5 Lakhs)** family floater per annum covering self, spouse, 2 children & dependent parents. | `🟢 High` |
| **Dental Coverage** | **Excluded**, unless necessitated by accidental facial trauma. Routine OPD/cosmetics not covered. | `🟢 High` |
| **Pre-Existing Diseases** | Covered after a waiting period of **24 consecutive months** of continuous employment. | `🟢 High` |
| **Cashless Claim Protocol** | TPA desk intimation at least **48 hours in advance** for planned, and within **24 hours** for emergency. | `🟢 High` |
| **Out-of-Scope (e.g. Pet Care)** | *"This information is not covered in the current company policies. Please contact HR directly at hr@company.com."* | `N/A (Grounded)` |

---

## 📁 Project Structure

```text
student-hr-rag-app/
├── data/
│   └── raw/
│       ├── hr_policy.md               # Leave policies, working hours, resignation
│       └── health_insurance_policy.md # Coverages, exclusions, network claims
├── db/
│   └── chroma_store/                  # Persistent ChromaDB vector database
├── docs/
│   ├── PRD.md                         # Product Requirement Document
│   ├── system-design.md               # System design & component architecture
│   ├── technical-plan.md              # Detailed implementation plan
│   └── copilot-guidance.md            # Mentorship & prompt engineering guidance
├── src/
│   ├── __init__.py
│   ├── ingest.py                      # Multi-format document parser, chunker & embedder
│   └── rag_engine.py                  # Semantic search, streaming generator & guardrails
├── .env.example                       # Template for API keys
├── .gitignore                         # Excludes secrets, pycache & local database files
├── app.py                             # Full-featured Streamlit chat UI
├── requirements.txt                   # Production dependencies
└── README.md                          # Project documentation
```

---

## 👥 Authors & Acknowledgements

- **Developed by:** Soma Nath & Krishna
- **Mentorship:** GeekyRahul (We4AI Gurukul Initiative)
- **Built with:** GitHub Copilot SDK, Google Gemini 3.8-Flash & Streamlit

---

<div align="center">
  <sub>⭐ If you find this project helpful, give it a star on GitHub!</sub>
</div>
