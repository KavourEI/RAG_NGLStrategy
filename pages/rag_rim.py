import os
import re
import streamlit as st
import tempfile

def render():
    # Lazy-import LlamaIndex bits only when needed
    try:
        from llama_cloud_services import LlamaCloudIndex
        from llama_index.llms.gemini import Gemini
    except ImportError as e:
        st.error(f"Missing dependency: {e}")
        st.stop()

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
        text = text.replace("$", r"\$")
        return text.strip()

    def format_for_markdown(text: str) -> str:
        if not text:
            return ""

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        for i, p in enumerate(paragraphs):
            paragraphs[i] = p.replace("\n", "  \n")
        return "\n\n".join(paragraphs)

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

    if "messages" not in st.session_state:
        st.session_state.messages = []

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
                <div class="data-source-item">📄 current.pdf</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)
        
        # Button positioned at bottom of container using negative margin
        st.markdown('<div style="margin-top: -70px; padding: 0 20px 20px 20px;">', unsafe_allow_html=True)
        
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
                                index = get_index()
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
                        
                        # Reset the uploader state
                        st.session_state.show_uploader = False
                        st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Center column - Main Chat Area
    with center_col:
        # Create a container for the chat area - height matches 70vh (~550px)
        chat_container = st.container(height=550, border=True)
        
        with chat_container:
            def render_message(message: dict):
                role = message.get("role", "")
                content = message.get("content", "") or ""

                if role == "user":
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    content_md = format_for_markdown(cleaned)
                    name = st.session_state.get("username") or "User"
                    st.markdown(f"**{name}:** {content_md}")

                elif role == "assistant":
                    name = "Bot"
                    with st.expander("🐛 Debug: View Raw Response", expanded=False):
                        st.code(content, language="text")
                    cleaned = clean_llm_response(content)
                    content_md = format_for_markdown(cleaned)
                    st.markdown(f"**{name}:** {content_md}")

                else:
                    cleaned = re.sub(r"\s+", " ", content).strip()
                    content_md = format_for_markdown(cleaned)
                    name = role.capitalize() or "User"
                    st.markdown(f"**{name}:** {content_md}")

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
                bot_msg = {"role": "assistant", "content": cleaned_response}
                st.session_state.messages.append(bot_msg)

            except Exception as e:
                error_msg = f"Error: {str(e)}"
                st.error(error_msg)
                err_msg = {"role": "assistant", "content": error_msg}
                st.session_state.messages.append(err_msg)
        
        st.rerun()
