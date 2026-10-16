# Student Copilot Guidance & Testing Guide

## 1. How to Build This App Using GitHub Copilot (Step-by-Step for First-Timers)

When building this application for the first time, you don't need to write all the boilerplate code yourself. Use GitHub Copilot as your coding partner by writing clear, explicit prompts (Context + Task).

### Prompting Tips for Copilot:
1. **For Ingestion (`src/ingest.py`):**
   * *Prompt to Copilot:* `"Write a Python script using ChromaDB and the google-genai SDK that reads all markdown files from data/raw/, splits them into paragraph chunks, generates embeddings using Gemini, and stores them in a local ChromaDB collection named hr_insurance_db."`
2. **For RAG Engine (`src/rag_engine.py`):**
   * *Prompt to Copilot:* `"Create a Python function query_rag(question: str) that loads the local ChromaDB collection, performs a similarity search for the question, retrieves the top 3 chunks, formats a prompt with this context, and calls Gemini (gemini-2.5-flash) to generate a grounded answer with citations."`
3. **For Streamlit UI (`app.py`):**
   * *Prompt to Copilot:* `"Write a Streamlit chat application where users can type HR and health insurance questions, view streaming answers from query_rag(), and see the retrieved source document snippets in an expander."`

---

## 2. Recommended Test Queries (To Validate Your RAG App)

Once your Streamlit app is running (`streamlit run app.py`), test your RAG system with these questions to verify it retrieves accurate answers without hallucinating:

1. **Leave Policy Test:**
   * *Query:* *"How many casual leaves do I get per year, and can I carry them forward?"*
   * *Expected Answer:* 12 casual leaves per year; they cannot be carried forward and lapse by December 31st.
2. **Maternity Leave Test:**
   * *Query:* *"What is the duration of maternity leave for female employees?"*
   * *Expected Answer:* 26 weeks of paid maternity leave for up to two surviving children.
3. **Health Insurance Sum Insured Test:**
   * *Query:* *"What is the total sum insured under our corporate health insurance policy?"*
   * *Expected Answer:* ₹5,00,000 (5 Lakhs) per employee family floater per annum.
4. **Dental & Cosmetic Exclusion Test:**
   * *Query:* *"Are routine dental checkups and teeth whitening covered under my insurance?"*
   * *Expected Answer:* No, routine dental checkups and cosmetic treatments are strictly excluded unless necessitated by accidental trauma.
5. **Pre-Existing Disease Waiting Period Test:**
   * *Query:* *"When does pre-existing disease coverage start for health insurance?"*
   * *Expected Answer:* Covered after a waiting period of 24 consecutive months of continuous employment.
