import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# Configure the page
st.set_page_config(
    page_title="NGL Strategy RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Clean CSS with proper font sizing and spacing
st.markdown("""
<style>
    /* Base reset for Cloud */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }
    
    /* Main app container */
    .stApp {
        background-color: #343541 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 14px !important;  /* Base font size */
        line-height: 1.5 !important;
    }
    
    /* Fix font sizes throughout the app */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        font-size: 14px !important;
        line-height: 1.5 !important;
        letter-spacing: normal !important;
        word-spacing: normal !important;
    }
    
    /* Fix oversized chat messages */
    .stChatMessage {
        padding: 12px 0 !important;
        margin: 0 !important;
    }
    
    .stChatMessage div {
        font-size: 14px !important;
        line-height: 1.5 !important;
        letter-spacing: normal !important;
    }
    
    /* Fix chat input */
    .stChatInputContainer textarea {
        font-size: 14px !important;
        line-height: 1.5 !important;
        padding: 12px !important;
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        border-radius: 8px !important;
    }
    
    /* Fix sidebar text */
    [data-testid="stSidebar"] * {
        font-size: 13px !important;
        line-height: 1.4 !important;
    }
    
    /* Fix headings */
    h1 {
        font-size: 24px !important;
        line-height: 1.3 !important;
        margin-bottom: 16px !important;
    }
    
    h2 {
        font-size: 20px !important;
        line-height: 1.3 !important;
        margin-bottom: 12px !important;
    }
    
    h3 {
        font-size: 16px !important;
        line-height: 1.3 !important;
        margin-bottom: 8px !important;
    }
    
    /* Fix button text */
    .stButton button {
        font-size: 13px !important;
        padding: 8px 16px !important;
    }
    
    /* Fix text input */
    .stTextInput input {
        font-size: 14px !important;
        padding: 8px 12px !important;
        line-height: 1.5 !important;
    }
    
    /* Fix spacing in lists */
    ul, ol {
        margin-top: 8px !important;
        margin-bottom: 8px !important;
        padding-left: 20px !important;
    }
    
    li {
        margin-bottom: 4px !important;
        line-height: 1.5 !important;
    }
    
    /* Fix paragraphs spacing */
    p {
        margin-bottom: 12px !important;
        line-height: 1.5 !important;
    }
    
    /* Fix code blocks */
    code {
        font-size: 12px !important;
        line-height: 1.4 !important;
    }
    
    /* Remove any excessive spacing */
    .block-container {
        padding-top: 20px !important;
        padding-bottom: 20px !important;
    }
    
    /* Mobile adjustments */
    @media (max-width: 768px) {
        .stApp {
            font-size: 15px !important;
        }
        
        .stChatMessage div {
            font-size: 15px !important;
        }
        
        .stChatInputContainer textarea {
            font-size: 15px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

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
        
        # Simple navigation
        if st.button("💬 Chat", use_container_width=True):
            st.session_state.page = "Chat"
            st.rerun()
        
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.page = "About"
            st.rerun()

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to NGL Strategy Assistant")
    st.markdown("### Please login to continue")
    
    st.markdown("""
    This AI assistant helps you explore and understand NGL Strategy documents through natural conversation.
    
    **Features:**
    - Natural language queries
    - Knowledge base powered by your documents
    - Accurate, contextual responses
    
    Login using the sidebar to get started.
    """)
    
else:
    if st.session_state.page == "About":
        st.title("NGL Strategy Assistant")
        
        st.markdown("""
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
        """)
        
    elif st.session_state.page == "Chat":
        try:
            from llama_cloud_services import LlamaCloudIndex
            from llama_index.llms.gemini import Gemini
            import re
            
            def clean_text(text):
                """Clean text for display with proper spacing"""
                if not text:
                    return ""
                # Remove excessive spaces
                text = re.sub(r'\s+', ' ', text)
                # Remove multiple newlines
                text = re.sub(r'\n\s*\n+', '\n\n', text)
                # Fix bullet points
                text = re.sub(r'^\s*[-•*]\s*', '• ', text, flags=re.MULTILINE)
                return text.strip()
            
            @st.cache_resource(show_spinner=False)
            def get_index():
                LLAMACLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')
                LLAMACLOUD_ORG_ID = os.getenv('LLAMA_ORG_ID')
                
                return LlamaCloudIndex(
                    name="NGL_Strategy",
                    project_name="Default",
                    organization_id=LLAMACLOUD_ORG_ID,
                    api_key=LLAMACLOUD_API_KEY
                )
            
            @st.cache_resource(show_spinner=False)
            def get_llm():
                return Gemini(
                    model="models/gemini-2.5-flash",
                    api_key=os.getenv("GOOGLE_API_KEY")
                )
            
            @st.cache_resource(show_spinner=False)
            def get_query_engine():
                index = get_index()
                llm = get_llm()
                return index.as_query_engine(llm=llm)
            
        except ImportError as e:
            st.error(f"Missing dependency: {e}")
            st.stop()
        
        st.title("Chat Assistant")
        
        # Initialize messages
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        prompt = st.chat_input("Ask a question about NGL Strategy...", key="chat_input")
        
        if prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        engine = get_query_engine()
                        response = engine.query(prompt)
                        
                        if hasattr(response, 'response'):
                            response_text = response.response
                        elif hasattr(response, 'text'):
                            response_text = response.text
                        else:
                            response_text = str(response)
                        
                        response_text = clean_text(response_text)
                        st.markdown(response_text)
                        st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear chat button
        if st.session_state.messages:
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
