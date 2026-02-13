"""
rag_rim.py - Streamlit page for RAG-based document assistant.

This module contains only Streamlit UI components.
All business logic is imported from functions.py for modularity.
"""

import re
import html
import streamlit as st

# Import all business logic from functions.py
from functions import (
    fetch_uploaded_documents,
    delete_document,
    upload_files_batch,
    create_llama_cloud_index,
    create_gemini_llm,
    create_query_engine,
    extract_response_text,
    extract_source_nodes,
)

# Configuration constants for UI
MAX_SOURCE_TEXT_LENGTH = 200  # Maximum characters to show from source text


def render():
    """Main render function for the RAG RIM page."""
    
    # ---------- Cached Resources ----------
    
    @st.cache_resource(show_spinner=False)
    def get_index():
        """Establish LlamaCloudIndex connection by setting up proper credentials."""
        return create_llama_cloud_index()

    @st.cache_resource(show_spinner=False)
    def get_llm():
        """Set up Gemini LLM with API key from environment."""
        return create_gemini_llm()

    @st.cache_resource(show_spinner=False)
    def get_query_engine():
        """Create and return a query engine that uses the cached index and LLM."""
        index = get_index()
        llm = get_llm()
        return create_query_engine(index=index, llm=llm)
    
    # ---------- Helper Functions for Document Management ----------
    
    def fetch_documents_with_error_handling():
        """Fetch documents with Streamlit error handling."""
        try:
            return fetch_uploaded_documents()
        except Exception as e:
            st.error(f"Error fetching documents: {str(e)}")
            return [{'name': 'current.pdf', 'id': None}]  # Fallback
    
    def handle_delete_document(file_id, file_name):
        """Handle document deletion with Streamlit UI feedback."""
        result = delete_document(file_id, file_name)
        if result['success']:
            st.success(result['message'])
            return True
        else:
            st.error(result['message'])
            return False
    
    def handle_upload_files(files):
        """Handle file upload with Streamlit UI feedback."""
        result = upload_files_batch(files)
        
        # Show success messages
        for file_name in result['success_files']:
            st.success(f"Uploaded {file_name}")
        
        # Show error messages
        for error in result['errors']:
            st.error(error)
        
        return result['success_files']

    # ---------- Chat UI ----------
    st.title("Rim Documents Assistant 🤖")
    
    # Initialize session state for messages and uploaded documents
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Fetch uploaded documents on first load or when not cached
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = fetch_documents_with_error_handling()
    
    # Layout: Chat column and Data column
    cols = st.columns([3, 1])
    chat_col, data_col = cols

    with chat_col:
        ## Chat Area
        chat_container = st.container(height=550, border=True)
        with chat_container:
            def render_message(message: dict):
                """Render a single chat message."""
                role = message.get("role", "")
                content = message.get("content", "") or ""
                sources = message.get("sources", [])

                if role == "user":
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    name = st.session_state.get("username") or "User"
                    st.markdown(f'<strong>{html.escape(name)}:</strong> {cleaned}', unsafe_allow_html=True)

                elif role == "assistant":
                    name = "Bot"
                    espace_content  = content.replace("$", "\\$")
                    st.markdown(f'<strong>{html.escape(name)}:</strong> {espace_content}', unsafe_allow_html=True)

                    if sources:
                        with st.expander("📚 Sources Used", expanded=False):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"**Source {idx}:** {source.get('file_name', 'Unknown')}")
                                if source.get('text'):
                                    text = source['text']
                                    preview = f"_{text[:MAX_SOURCE_TEXT_LENGTH]}..._" if len(
                                        text) > MAX_SOURCE_TEXT_LENGTH else f"_{text}_"
                                    st.markdown(preview)
                                st.markdown("---")

                else:
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    name = role.capitalize() or "User"
                    st.markdown(f'<strong>{html.escape(name)}:</strong> {cleaned}', unsafe_allow_html=True)

            for msg in st.session_state.messages:
                render_message(msg)

        prompt = st.chat_input("Ask a question about NGL Strategy...", key="chat_input")

        if st.session_state.messages:
            if st.button("Clear Chat History", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    with data_col:
        ## Uploaded Documents Section
        st.subheader("Data Used")

        if 'uploaded_documents' not in st.session_state:
            st.session_state.uploaded_documents = fetch_documents_with_error_handling()

        # Display document list with delete buttons
        for idx, doc in enumerate(st.session_state.uploaded_documents):
            doc_name = doc['name'] if isinstance(doc, dict) else doc
            doc_id = doc.get('id') if isinstance(doc, dict) else None

            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📄 {doc_name}")
            with col2:
                if doc_id:
                    if st.button("🗑️", key=f"delete_{idx}", help=f"Delete {doc_name}"):
                        if handle_delete_document(doc_id, doc_name):
                            st.session_state.uploaded_documents = fetch_documents_with_error_handling()
                            st.rerun()

        ## Document Uploader Section
        if "show_uploader" not in st.session_state:
            st.session_state.show_uploader = False

        if st.button("Attach new Documents", use_container_width=True, type="primary", key="attach_btn"):
            st.session_state.show_uploader = not st.session_state.show_uploader

        if st.session_state.show_uploader:
            st.info("Upload PDF or DOCX files")
            new_data = st.file_uploader("Choose files", type=["pdf", "docx"], accept_multiple_files=True,
                                        key="file_uploader")

            if new_data and st.button("Upload to Index", key="upload_btn", type="primary",
                                      use_container_width=True):
                with st.spinner("Uploading files..."):
                    uploaded_files = handle_upload_files(new_data)

                    if uploaded_files:
                        st.balloons()
                        st.success(
                            f"Successfully uploaded {len(uploaded_files)} file(s): {', '.join(uploaded_files)}")
                        st.session_state.uploaded_documents = fetch_documents_with_error_handling()

                    st.session_state.show_uploader = False
                    st.rerun()

    # Handle user input/query
    if prompt:
        user_msg = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_msg)

        with st.spinner("Thinking..."):
            try:
                engine = get_query_engine()
                response = engine.query(prompt)

                response_text = extract_response_text(response)
                sources = extract_source_nodes(response)
                
                bot_msg = {"role": "assistant", "content": response_text, "sources": sources}
                st.session_state.messages.append(bot_msg)

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                err_msg = {"role": "assistant", "content": error_msg}
                st.session_state.messages.append(err_msg)
        
        st.rerun()
