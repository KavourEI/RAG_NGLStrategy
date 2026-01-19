import os
import re
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="NGL Strategy RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Clean CSS (placeholder – add your CSS if needed)
st.markdown(
    """
""",
    unsafe_allow_html=True,
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "page" not in st.session_state:
    st.session_state.page = "Chat"

# Sidebar
with st.sidebar:
    st.title("NGL Strategy")

    if not st.session_state.authenticated:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", type="primary"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Please enter username and password")
    else:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

    st.divider()

    # Simple navigation - use plain text labels (no emojis)
    if st.button("Chat", use_container_width=True):
        st.session_state.page = "Chat"
        st.rerun()

    if st.button("About", use_container_width=True):
        st.session_state.page = "About"
        st.rerun()

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to NGL Strategy Assistant")
    st.markdown("### Please login to continue")
    st.markdown(
        """
This AI assistant helps you explore and understand NGL Strategy documents through natural conversation.

**Features:**
- Natural language queries
- Knowledge base powered by your documents
- Accurate, contextual responses

Login using the sidebar to get started.
"""
    )

else:
    if st.session_state.page == "About":
        st.title("NGL Strategy Assistant")
        st.markdown(
            """
### Welcome to your AI-powered NGL Strategy assistant

This assistant uses advanced AI to help you quickly find information that is stored in RIM Documents.  
Ask questions and get instant, accurate answers based on the aforementioned knowledge base.

---

#### How it works

**Document Understanding** Your documents are indexed and processed to enable intelligent search and retrieval of relevant information.  
**Context-Aware Responses** The AI analyzes your question along with relevant document sections to provide accurate, contextual answers.  
**Natural Conversation** Chat naturally with your knowledge base - ask follow-up questions and explore topics in depth.

---

#### Key Features

🔍 **Semantic Search** - Find information based on meaning, not just keywords  
🧠 **AI-Powered Analysis** - Get intelligent summaries and insights  
⚡ **Instant Answers** - Quick responses from your document library  
💬 **Conversational** - Ask questions in natural language  

---

#### Technology

This assistant is powered by:
- **LlamaCloud** for document indexing and retrieval
- **Google Gemini (gemini-2.5-flash)** for natural language understanding
- **LlamaIndex** for RAG orchestration

---

**Ready to start?** Navigate to the Chat page to begin asking questions.
"""
        )

    elif st.session_state.page == "Chat":
        # Lazy-import LlamaIndex bits only when needed
        try:
            from llama_cloud_services import LlamaCloudIndex
            from llama_index.llms.gemini import Gemini
        except ImportError as e:
            st.error(f"Missing dependency: {e}")
            st.stop()

        # ---------- Cleaning helpers ----------

        def clean_llm_response(text: str) -> str:
            """Light cleaning of LLM responses without breaking layout."""
            if not text:
                return ""

            # Normalize dashes
            text = (
                text.replace("−", "-")
                .replace("‑", "-")
                .replace("–", "-")
                .replace("—", "-")
            )

            # Collapse extra spaces in lines
            text = re.sub(r"[ \t]+", " ", text)

            # Normalize multiple blank lines to a single blank line
            text = re.sub(r"\n\s*\n+", "\n\n", text)

            # Fix numeric ranges like "639 - 649"
            text = re.sub(r"(\d)\s*-\s*(\d)", r"\1-\2", text)

            # Space after punctuation when missing
            text = re.sub(r"([.,!?;:])([A-Za-z])", r"\1 \2", text)

            return text.strip()

        def format_for_markdown(text: str) -> str:
            """Preserve paragraphs and soft line breaks for Streamlit markdown."""
            if not text:
                return ""

            # Split paragraphs on blank lines
            paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
            for i, p in enumerate(paragraphs):
                # Inside a paragraph, treat single \n as markdown line break
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

        # Initialize messages
        if "messages" not in st.session_state:
            st.session_state.messages = []

        def render_message(message: dict):
            role = message.get("role", "")
            content = message.get("content", "") or ""

            if role == "assistant":
                cleaned = clean_llm_response(content)
            else:
                # Normalize user whitespace but keep it readable
                cleaned = re.sub(r"\s+", " ", content).strip()

            content_md = format_for_markdown(cleaned)

            if role == "user":
                name = st.session_state.get("username") or "User"
            elif role == "assistant":
                name = "Bot"
            else:
                name = role.capitalize() or "User"

            st.markdown(f"**{name}**")
            st.markdown(content_md)

        # Render history
        for msg in st.session_state.messages:
            render_message(msg)

        # Chat input
        prompt = st.chat_input(
            "Ask a question about NGL Strategy...", key="chat_input"
        )

        if prompt:
            user_msg = {"role": "user", "content": prompt}
            st.session_state.messages.append(user_msg)
            render_message(user_msg)

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
                    render_message(bot_msg)
                    st.session_state.messages.append(bot_msg)

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    err_msg = {"role": "assistant", "content": error_msg}
                    st.session_state.messages.append(err_msg)
                    render_message(err_msg)

        # Clear chat button
        if st.session_state.messages:
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
