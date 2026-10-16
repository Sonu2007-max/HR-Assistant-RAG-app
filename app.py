"""
Streamlit Web UI: Enterprise HR & Health Insurance RAG Assistant
Complete end-to-end working prototype with:
- Dynamic PDF/TXT/MD document upload & indexing
- Real-time token streaming with Gemini 3.8-Flash
- Category filtering & Top-K retrieval controls
- Anti-hallucination source citations with relevance scores
- One-click FAQ prompt buttons
- Chat history reset and markdown export
"""

import os
from datetime import datetime
import streamlit as st
from src.rag_engine import query_rag_stream
from src.ingest import (
    add_document_to_store,
    get_indexed_stats,
    ingest_documents
)

# Page Configuration
st.set_page_config(
    page_title="Enterprise HR & Health Insurance Assistant",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling
st.markdown("""
<style>
    /* Header Styling */
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .badge-pill {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        margin-right: 0.4rem;
        margin-bottom: 0.6rem;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
        background-color: #E0E7FF;
        color: #3730A3;
    }
    .badge-green {
        background-color: #DCFCE7;
        color: #166534;
    }
    .badge-blue {
        background-color: #DBEAFE;
        color: #1E40AF;
    }
    .sub-title {
        font-size: 0.95rem;
        color: #4B5563;
        margin-bottom: 1rem;
    }
    /* Citation Card */
    .citation-box {
        background: #F9FAFB;
        border-left: 3px solid #3B82F6;
        padding: 0.6rem 0.8rem;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
        border-radius: 4px;
        font-size: 0.88rem;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.markdown("## ⚙️ Control Panel")

    # Ingestion & Knowledge Base Overview
    st.subheader("📚 Knowledge Base")
    stats = get_indexed_stats()
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Chunks", stats["total_chunks"])
    with col2:
        st.metric("Documents", len(stats["documents"]))

    with st.expander("📄 Indexed Documents", expanded=False):
        if stats["documents"]:
            for doc, info in stats["documents"].items():
                st.markdown(f"• **`{doc}`**")
                st.caption(f"Category: *{info['category']}* | Chunks: {info['count']}")
        else:
            st.info("No documents currently indexed.")

    st.divider()

    # Upload New Policy Document (PDF, MD, TXT)
    st.subheader("📤 Upload New Policy")
    uploaded_file = st.file_uploader(
        "Upload Policy Document (.pdf, .md, .txt)",
        type=["pdf", "md", "txt"],
        help="Upload company HR policies, medical handbooks, or FAQs to index dynamically."
    )
    category_choice = st.selectbox(
        "Assign Policy Category",
        ["Auto-Detect", "HR & Leaves", "Health Insurance", "General Policies"]
    )

    if uploaded_file is not None:
        if st.button("🚀 Ingest Document", use_container_width=True):
            with st.spinner(f"Parsing and indexing '{uploaded_file.name}'..."):
                try:
                    chosen_cat = None if category_choice == "Auto-Detect" else category_choice
                    num_chunks = add_document_to_store(
                        filename=uploaded_file.name,
                        file_bytes=uploaded_file.getvalue(),
                        category=chosen_cat
                    )
                    st.success(f"Successfully indexed '{uploaded_file.name}' into {num_chunks} chunks!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error during ingestion: {str(e)}")

    if st.button("🔄 Reset Default Knowledge Base", use_container_width=True):
        with st.spinner("Re-indexing default policy documents..."):
            ingest_documents()
            st.success("Knowledge Base reset to default policies!")
            st.rerun()

    st.divider()

    # Search & Retrieval Configuration
    st.subheader("🔍 Retrieval Settings")
    available_categories = ["All Policies"] + stats.get("categories", [])
    selected_category = st.selectbox("Policy Category Filter", available_categories, index=0)
    top_k = st.slider("Top Relevant Chunks (K)", min_value=2, max_value=5, value=3)

    st.divider()

    # Chat Actions
    st.subheader("💬 Chat Management")
    if st.button("🧹 Clear Conversation", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Namaste! Main aapka HR & Health Insurance Assistant hoon. Company policies ya insurance claims se juda koi bhi sawal poochiye."
            }
        ]
        st.rerun()

    # Export Chat Transcript
    if "messages" in st.session_state and len(st.session_state.messages) > 1:
        transcript = f"# HR Assistant Chat Transcript - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        for m in st.session_state.messages:
            role_label = "Employee" if m["role"] == "user" else "HR Assistant"
            transcript += f"### {role_label}:\n{m['content']}\n\n"
        st.download_button(
            label="📥 Export Chat (Markdown)",
            data=transcript,
            file_name=f"hr_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )


# Main Interface Header
st.markdown('<div class="main-title">🏢 Enterprise HR & Health Insurance Assistant</div>', unsafe_allow_html=True)
st.markdown("""
<div>
    <span class="badge-pill badge-green">⚡ Gemini 3.8-Flash</span>
    <span class="badge-pill badge-blue">🔍 ChromaDB Vector Engine</span>
    <span class="badge-pill">🛡️ Anti-Hallucination Grounded</span>
</div>
<div class="sub-title">Ask verified questions about leave policies, medical insurance coverage, network cashless claims, and waiting periods.</div>
""", unsafe_allow_html=True)

# Sample Quick Query Buttons
st.markdown("##### 💡 Suggested Questions")
faq_cols = st.columns(4)
sample_queries = [
    "Duration of maternity leave?",
    "Total sum insured under health policy?",
    "Are pre-existing diseases covered?",
    "How to claim cashless hospitalization?"
]

for idx, sq in enumerate(sample_queries):
    col = faq_cols[idx % 4]
    if col.button(sq, key=f"faq_btn_{idx}", use_container_width=True):
        st.session_state["user_input_override"] = sq

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Namaste! Main aapka HR & Health Insurance Assistant hoon. Company policies ya insurance claims se juda koi bhi sawal poochiye."
        }
    ]

# Render Existing Messages
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("📚 View Source Citations"):
                for src in msg["sources"]:
                    relevance_emoji = "🟢" if src.get("relevance") == "High" else "🟡"
                    st.markdown(
                        f"**Document:** `{src['source']}` &nbsp;|&nbsp; "
                        f"**Category:** `{src.get('category', 'General')}` &nbsp;|&nbsp; "
                        f"**Chunk #{src['chunk_id']}** &nbsp;|&nbsp; "
                        f"**Relevance:** {relevance_emoji} {src.get('relevance', 'Match')} (dist: {src.get('distance', 'N/A')})"
                    )
                    st.caption(f"_{src['snippet']}_")
                    st.divider()

# Input Handling
prompt = st.chat_input("Type your HR or Health Insurance question here...")

# Handle click from suggested FAQ buttons
if "user_input_override" in st.session_state:
    prompt = st.session_state.pop("user_input_override")

if prompt:
    # Append user question
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # Process query through RAG engine with token streaming
    with st.chat_message("assistant", avatar="🤖"):
        category_param = None if selected_category == "All Policies" else selected_category
        try:
            stream_gen, sources = query_rag_stream(
                question=prompt,
                top_k=top_k,
                category_filter=category_param,
                chat_history=st.session_state.messages[:-1]
            )

            # Stream response in real time
            full_response = st.write_stream(stream_gen)

            # Display citations
            if sources:
                with st.expander("📚 View Source Citations"):
                    for src in sources:
                        relevance_emoji = "🟢" if src.get("relevance") == "High" else "🟡"
                        st.markdown(
                            f"**Document:** `{src['source']}` &nbsp;|&nbsp; "
                            f"**Category:** `{src.get('category', 'General')}` &nbsp;|&nbsp; "
                            f"**Chunk #{src['chunk_id']}** &nbsp;|&nbsp; "
                            f"**Relevance:** {relevance_emoji} {src.get('relevance', 'Match')} (dist: {src.get('distance', 'N/A')})"
                        )
                        st.caption(f"_{src['snippet']}_")
                        st.divider()

            # Save assistant response with sources
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "sources": sources
            })

        except Exception as e:
            error_msg = f"⚠️ Error: {str(e)}"
            st.error(error_msg)
            st.session_state.messages.append({
                "role": "assistant",
                "content": error_msg
            })

