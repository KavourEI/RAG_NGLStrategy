import os
import re
import streamlit as st
import tempfile
import requests

def render():
    # Lazy-import LlamaIndex bits only when needed
    try:
        from llama_index.indices.managed.llama_cloud import LlamaCloudIndex
        from llama_index.llms.gemini import Gemini
    except ImportError as e:
        st.error(f"Missing dependency: {e}")
        st.stop()

    # Configuration constants
    PIPELINE_ID = os.getenv("LLAMA_PIPELINE_ID", "70fa557d-916f-4372-9dd7-d85457059f10")
    MAX_SOURCE_TEXT_LENGTH = 200  # Maximum characters to show from source text
    
    # ---------- Cleaning helpers ----------

    def _collapse_single_char_lines(raw: str) -> str:
        if not raw:
            return ""

        lines = raw.split("\n")
        out = []
        buf = []

        def flush_buf():
            nonlocal out, buf
            if not buf:
                return
            s = "".join(buf)
            s = re.sub(r"\s*([,./])\s*", r"\1", s)
            s = re.sub(r"\s*([-])\s*", r"\1", s)
            out.append(s)
            buf = []

        for line in lines:
            t = line.strip()
            if len(t) == 1:
                buf.append(t)
            else:
                flush_buf()
                out.append(t)

        flush_buf()
        return "\n".join(out)

    def clean_llm_response(text: str) -> str:
        if not text:
            return ""

        text = _collapse_single_char_lines(text)

        text = (
            text.replace("−", "-")
                .replace("‑", "-")
                .replace("–", "-")
                .replace("—", "-")
        )

        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n\s*\n+", "\n\n", text)
        text = re.sub(r"(\d)\s*-\s*(\d)", r"\1-\2", text)
        text = re.sub(r"(\d)/(mt)\b", r"\1/mt", text)
        text = re.sub(r"(\d/mt)([A-Za-z])", r"\1 \2", text)
        text = re.sub(r"\bmtto\b", "mt to", text)
        text = re.sub(r"([.,!?;:])([A-Za-z])", r"\1 \2", text)
        # Don't escape dollar signs here - we'll handle them in HTML rendering
        return text.strip()

    def format_for_markdown(text: str) -> str:
        if not text:
            return ""

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for i, p in enumerate(paragraphs):
            paragraphs[i] = p.replace("\n", "  \n")
        return "\n\n".join(paragraphs)
    
    def escape_html(text: str) -> str:
        """Escape HTML entities to prevent unwanted rendering"""
        if not text:
            return ""
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                    .replace('"', "&quot;")
                    .replace("'", "&#39;"))

    # ---------- LlamaCloud Document Fetching ----------

    def fetch_uploaded_documents():
        """Fetch list of uploaded documents from LlamaCloud API"""
        try:
            url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{PIPELINE_ID}/files2"
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                # Extract file info from the response (both name and id)
                files = data.get('files', [])
                return [{'name': file.get('name', 'Unknown'), 'id': file.get('id')} for file in files]
            else:
                # Include response details in error message for debugging
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                st.error(f"Failed to fetch documents (status {response.status_code}): {error_detail}")
                return [{'name': 'current.pdf', 'id': None}]  # Fallback to default
        except requests.RequestException as e:
            st.error(f"Network error fetching documents: {str(e)}")
            return [{'name': 'current.pdf', 'id': None}]  # Fallback to default
        except Exception as e:
            st.error(f"Unexpected error fetching documents: {str(e)}")
            return [{'name': 'current.pdf', 'id': None}]  # Fallback to default

    def delete_document(file_id: str, file_name: str):
        """Delete a document from LlamaCloud"""
        try:
            url = f"https://api.cloud.llamaindex.ai/api/v1/pipelines/{PIPELINE_ID}/files/{file_id}"
            
            headers = {
                'Accept': 'application/json',
                'Authorization': f'Bearer {os.getenv("LLAMA_CLOUD_API_KEY")}'
            }
            
            response = requests.delete(url, headers=headers)
            
            if response.status_code in [200, 204]:
                st.success(f"Successfully deleted {file_name}")
                return True
            else:
                try:
                    error_detail = response.json()
                except:
                    error_detail = response.text
                st.error(f"Failed to delete {file_name} (status {response.status_code}): {error_detail}")
                return False
        except requests.RequestException as e:
            st.error(f"Network error deleting {file_name}: {str(e)}")
            return False
        except Exception as e:
            st.error(f"Unexpected error deleting {file_name}: {str(e)}")
            return False

    # ---------- LlamaIndex resources ----------

    @st.cache_resource(show_spinner=False)
    def get_index():
        LLAMACLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")
        LLAMACLOUD_ORG_ID = os.getenv("LLAMA_ORG_ID")
        return LlamaCloudIndex(
            name="NGL_Strategy",
            project_name="Default",
            organization_id=LLAMACLOUD_ORG_ID,
            api_key=LLAMACLOUD_API_KEY,
        )

    @st.cache_resource(show_spinner=False)
    def get_llm():
        return Gemini(
            model="models/gemini-2.5-flash",
            api_key=os.getenv("GOOGLE_API_KEY"),
        )

    @st.cache_resource(show_spinner=False)
    def get_query_engine():
        index = get_index()
        llm = get_llm()
        return index.as_query_engine(llm=llm)

    # ---------- Chat UI ----------
    st.title("Chat Assistant")
    
    # Initialize session state for messages and uploaded documents
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Fetch uploaded documents on first load or when not cached
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = fetch_uploaded_documents()
    
    # Add custom CSS for rounded containers
    st.markdown("""
        <style>
        /* Reduce main app container height */
        .stAppViewBlockContainer, .block-container, .ea3mdgi5 {
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            max-height: 85vh !important;
        }
        
        .side-container {
            background-color: #2E3B4E;
            border-radius: 20px;
            padding: 20px;
            height: 70vh;
            display: flex;
            flex-direction: column;
        }
        .container-title {
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            color: #FFFFFF;
            padding-bottom: 10px;
        }
        .container-divider {
            border-top: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 15px;
        }
        .chat-list-item {
            background-color: transparent;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 10px;
            cursor: pointer;
            transition: background-color 0.2s;
            color: #FFFFFF;
        }
        .chat-list-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .data-source-item {
            background-color: transparent;
            border-radius: 8px;
            padding: 10px;
            margin-bottom: 8px;
            font-size: 14px;
            color: #FFFFFF;
        }
        .container-content {
            flex: 1;
            overflow-y: auto;
        }
        .container-bottom {
            margin-top: auto;
            padding-top: 10px;
        }
        .center-container {
            background-color: #2E3B4E;
            border-radius: 20px;
            padding: 20px;
            height: 70vh;
            display: flex;
            flex-direction: column;
        }
        .chat-messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 10px;
            margin-bottom: 10px;
        }
        .chat-message {
            margin-bottom: 15px;
            color: #FFFFFF;
        }
        .chat-message strong {
            color: #4DA6FF;
        }
        /* Style the center chat container to match side containers */
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
            height: 70vh !important;
        }
        div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] > div {
            height: 100% !important;
        }
        </style>
    """, unsafe_allow_html=True)

    # Create two-column layout (left container commented out)
    # left_col, center_col, right_col = st.columns([1, 2, 1])
    center_col, right_col = st.columns([3, 1])
    
    # Left container - Chat Library (commented out)
    # with left_col:
    #     st.markdown('''
    #     <div class="side-container">
    #         <div class="container-title">Library</div>
    #         <div class="container-divider"></div>
    #         <div class="container-content">
    #             <div class="chat-list-item">📁 Rim Documents</div>
    #         </div>
    #     </div>
    #     ''', unsafe_allow_html=True)
    
    # Right container - Data Sources
    with right_col:
        st.markdown('''
        <div class="side-container">
            <div class="container-title">Data Used</div>
            <div class="container-divider"></div>
            <div class="container-content">
        ''', unsafe_allow_html=True)
        
        # Display documents with delete buttons in a scrollable area inside the container
        for idx, doc in enumerate(st.session_state.uploaded_documents):
            doc_name = doc['name'] if isinstance(doc, dict) else doc
            doc_id = doc.get('id') if isinstance(doc, dict) else None
            
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f'<div style="color: #FFFFFF; padding: 5px 0;">📄 {doc_name}</div>', unsafe_allow_html=True)
            with col2:
                if doc_id:
                    if st.button("🗑️", key=f"delete_{idx}", help=f"Delete {doc_name}"):
                        if delete_document(doc_id, doc_name):
                            # Refresh the document list
                            st.session_state.uploaded_documents = fetch_uploaded_documents()
                            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)  # Close container-content
        
        # Button positioned at bottom of container
        st.markdown('<div class="container-bottom">', unsafe_allow_html=True)
        
        # Initialize session state for uploader visibility
        if "show_uploader" not in st.session_state:
            st.session_state.show_uploader = False
        
        # Main button to show uploader
        if st.button("Attach new Documents", use_container_width=True, type="primary", key="attach_btn"):
            st.session_state.show_uploader = not st.session_state.show_uploader
        
        # File uploader (only shown when show_uploader is True)
        if st.session_state.show_uploader:
            st.info("Upload PDF or DOCX files")
            new_data = st.file_uploader("Choose files", type=["pdf", "docx"], 
                                       accept_multiple_files=True, key="file_uploader")
            
            if new_data:
                if st.button("Upload to Index", key="upload_btn", type="primary", use_container_width=True):
                    with st.spinner("Uploading files..."):
                        uploaded_files = []
                        for f in new_data:
                            temp_dir = tempfile.mkdtemp()
                            file_path = os.path.join(temp_dir, f.name)
                            with open(file_path, "wb") as temp_file:
                                temp_file.write(f.getbuffer())
                            
                            try:
                                # Use the working upload_file method
                                index = LlamaCloudIndex(
                                    name="NGL_Strategy",
                                    project_name="Default",
                                    organization_id="44ae1ea1-e4cb-4a16-b55e-9024ef961a7c",
                                    api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
                                    )
                                index.upload_file(file_path=file_path)
                                uploaded_files.append(f.name)
                                st.success(f"Uploaded {f.name}")
                            except Exception as e:
                                st.error(f"Error uploading {f.name}: {str(e)}")
                            finally:
                                # Clean up temporary file
                                import shutil
                                try:
                                    os.remove(file_path)
                                    os.rmdir(temp_dir)
                                except:
                                    pass
                        
                        if uploaded_files:
                            st.balloons()
                            st.success(f"Successfully uploaded {len(uploaded_files)} file(s): {', '.join(uploaded_files)}")
                            # Refresh the uploaded documents list
                            st.session_state.uploaded_documents = fetch_uploaded_documents()
                        
                        # Reset the uploader state
                        st.session_state.show_uploader = False
                        st.rerun()
        
        st.markdown('</div></div>', unsafe_allow_html=True)  # Close container-bottom and side-container
    
    # Center column - Main Chat Area
    with center_col:
        # Create a container for the chat area - height matches 70vh (~550px)
        chat_container = st.container(height=550, border=True)
        
        with chat_container:
            def render_message(message: dict):
                role = message.get("role", "")
                content = message.get("content", "") or ""
                sources = message.get("sources", [])

                if role == "user":
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    content_md = format_for_markdown(cleaned)
                    content_html = escape_html(content_md).replace("  \n", "<br>")
                    # Handle paragraphs: split by \n\n and wrap each in <p> tags
                    paragraphs = [f"<p>{p}</p>" for p in content_html.split("\n\n") if p.strip()]
                    content_html = "".join(paragraphs)
                    name = st.session_state.get("username") or "User"
                    st.markdown(f'<strong>{escape_html(name)}:</strong> {content_html}', unsafe_allow_html=True)

                elif role == "assistant":
                    name = "Bot"
                    with st.expander("🐛 Debug: View Raw Response", expanded=False):
                        st.code(content, language="text")
                    cleaned = clean_llm_response(content)
                    content_md = format_for_markdown(cleaned)
                    content_html = escape_html(content_md).replace("  \n", "<br>")
                    # Handle paragraphs: split by \n\n and wrap each in <p> tags
                    paragraphs = [f"<p>{p}</p>" for p in content_html.split("\n\n") if p.strip()]
                    content_html = "".join(paragraphs)
                    st.markdown(f'<strong>{escape_html(name)}:</strong> {content_html}', unsafe_allow_html=True)
                    
                    # Display sources if available
                    if sources:
                        with st.expander("📚 Sources Used", expanded=False):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"**Source {idx}:** {source.get('file_name', 'Unknown')}")
                                if source.get('text'):
                                    text = source['text']
                                    preview = f"_{text[:MAX_SOURCE_TEXT_LENGTH]}..._" if len(text) > MAX_SOURCE_TEXT_LENGTH else f"_{text}_"
                                    st.markdown(preview)
                                st.markdown("---")

                else:
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    content_md = format_for_markdown(cleaned)
                    content_html = escape_html(content_md).replace("  \n", "<br>")
                    # Handle paragraphs: split by \n\n and wrap each in <p> tags
                    paragraphs = [f"<p>{p}</p>" for p in content_html.split("\n\n") if p.strip()]
                    content_html = "".join(paragraphs)
                    name = role.capitalize() or "User"
                    st.markdown(f'<strong>{escape_html(name)}:</strong> {content_html}', unsafe_allow_html=True)

            for msg in st.session_state.messages:
                render_message(msg)
        
        # Chat input at the bottom
        prompt = st.chat_input(
            "Ask a question about NGL Strategy...", key="chat_input"
        )
        
        # Clear chat button
        if st.session_state.messages:
            if st.button("Clear Chat History", type="secondary", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    if prompt:
        user_msg = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_msg)

        with st.spinner("Thinking..."):
            try:
                engine = get_query_engine()
                response = engine.query(prompt)

                if hasattr(response, "response"):
                    response_text = response.response
                elif hasattr(response, "text"):
                    response_text = response.text
                else:
                    response_text = str(response)

                cleaned_response = clean_llm_response(response_text)
                
                # Extract source information
                sources = []
                if hasattr(response, "source_nodes"):
                    for node in response.source_nodes:
                        source_info = {
                            'file_name': node.node.metadata.get('file_name', 'Unknown'),
                            'text': node.node.text if hasattr(node.node, 'text') else '',
                            'score': node.score if hasattr(node, 'score') else None
                        }
                        sources.append(source_info)
                
                bot_msg = {"role": "assistant", "content": cleaned_response, "sources": sources}
                st.session_state.messages.append(bot_msg)

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                err_msg = {"role": "assistant", "content": error_msg}
                st.session_state.messages.append(err_msg)
        
        st.rerun()
