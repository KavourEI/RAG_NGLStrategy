import os
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

# Configure the page - USE UNICODE EMOJI DIRECTLY, NOT SHORTCODES
st.set_page_config(
    page_title="NGL Strategy RAG Assistant",
    page_icon="🤖",  # Unicode emoji, not shortcode
    layout="wide",
    initial_sidebar_state="expanded"
)

# IMPORTANT: Inject CSS early and use !important aggressively for Cloud
st.markdown("""
<style>
    /* Reset and base styles for Cloud compatibility */
    :root {
        --sidebar-width: 336px;
        --content-max-width: 1075px;
        --bottom-padding: 150px;
        --base-font-size: 16px;
        --is-mobile: 0;
    }

    /* Force dark theme for Cloud */
    .stApp {
        background-color: #343541 !important;
        color-scheme: dark !important;
    }

    /* Fix emoji display - ensure emoji fonts are available */
    * {
        font-family: 'Segoe UI Emoji', 'Apple Color Emoji', 'Noto Color Emoji', 
                     'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* Fix chat input background - override Cloud's theme */
    .stChatInputContainer {
        background-color: transparent !important;
    }
    
    .stChatInputContainer textarea {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        width: 100% !important;
        max-width: var(--content-max-width) !important;
        margin: 0 auto !important;
        display: block !important;
    }

    /* Fix sidebar width and positioning */
    section[data-testid="stSidebar"] {
        min-width: 250px !important;
        max-width: 450px !important;
        width: var(--sidebar-width) !important;
    }

    /* Force hide Streamlit Cloud branding and theme overrides */
    .stDeployButton { display: none !important; }
    iframe { display: none !important; }
    
    /* Ensure chat messages container has proper spacing */
    [data-testid="stChatMessageContainer"] {
        padding-bottom: 120px !important;
    }

    /* Mobile responsiveness */
    @media (max-width: 768px) {
        :root {
            --sidebar-width: 0px !important;
            --content-max-width: 100% !important;
        }
        
        section[data-testid="stSidebar"] {
            transform: translateX(-100%) !important;
        }
        
        .stChatInputContainer {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        
        .stChatInputContainer textarea {
            width: 100% !important;
            max-width: 100% !important;
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

# Sidebar - SIMPLIFIED for Cloud compatibility
with st.sidebar:
    st.title("📊 NGL Strategy")  # Unicode emoji
    
    if not st.session_state.authenticated:
        st.subheader("🔐 Login")  # Unicode emoji
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login", type="primary"):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome, {username}! ✅")  # Unicode emoji
                st.rerun()
            else:
                st.error("❌ Please enter username and password")
    else:
        st.success(f"👤 Logged in as: {st.session_state.username}")
        
        if st.button("Logout", type="secondary"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()
        
        st.divider()
        
        # Navigation using buttons instead of radio for better Cloud compatibility
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💬 Chat", use_container_width=True):
                st.session_state.page = "Chat"
                st.rerun()
        with col2:
            if st.button("ℹ️ About", use_container_width=True):
                st.session_state.page = "About"
                st.rerun()
        
        # Visual indicator
        st.markdown(f"**Current page:** {st.session_state.page}")

# Main content area
if not st.session_state.authenticated:
    st.title("🤖 Welcome to NGL Strategy Assistant")
    st.markdown("### 🔒 Please login to continue")
    
    st.markdown("""
    This AI assistant helps you explore and understand NGL Strategy documents through natural conversation.
    
    **✨ Features:**
    - 💬 Natural language queries
    - 📚 Knowledge base powered by your documents
    - 🎯 Accurate, contextual responses
    
    Login using the sidebar to get started.
    """)
    
else:
    if st.session_state.page == "About":
        st.title("📚 NGL Strategy Assistant")
        
        st.markdown("""
        ### 🎯 Welcome to your AI-powered NGL Strategy assistant
        
        This assistant uses advanced AI to help you quickly find information that is stored in RIM Documents. 
        Ask questions and get instant, accurate answers based on the aforementioned knowledge base.
        
        ---
        
        #### ⚙️ How it works
        
        **📄 Document Understanding** Your documents are indexed and processed to enable intelligent search and retrieval of relevant information.
        
        **🧠 Context-Aware Responses** The AI analyzes your question along with relevant document sections to provide accurate, contextual answers.
        
        **💭 Natural Conversation** Chat naturally with your knowledge base - ask follow-up questions and explore topics in depth.
        
        ---
        
        #### ✨ Key Features
        
        🔍 **Semantic Search** - Find information based on meaning, not just keywords  
        🧠 **AI-Powered Analysis** - Get intelligent summaries and insights  
        ⚡ **Instant Answers** - Quick responses from your document library  
        💬 **Conversational** - Ask questions in natural language  
        
        ---
        
        #### 🛠️ Technology
        
        This assistant is powered by:
        - **LlamaCloud** for document indexing and retrieval
        - **Google Gemini (gemini-2.5-flash)** for natural language understanding
        - **LlamaIndex** for RAG orchestration
        
        ---
        
        **🚀 Ready to start?** Navigate to the Chat page to begin asking questions.
        """)
        
    elif st.session_state.page == "Chat":
        # Import inside the page to avoid loading issues if dependencies missing
        try:
            from llama_cloud_services import LlamaCloudIndex
            from llama_index.llms.gemini import Gemini
            import re
            
            def clean_text(text):
                """Clean text for display"""
                if not text:
                    return ""
                text = re.sub(r'\*+', '', text)
                text = re.sub(r'[−‑–—]', '-', text)
                text = re.sub(r' +', ' ', text)
                text = re.sub(r'\n\s*\n+', '\n\n', text)
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
            st.error(f"❌ Missing dependency: {e}")
            st.stop()
        
        st.title("💬 Chat Assistant")
        
        # Initialize messages in session state
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input - USING st.chat_input with custom container styling
        prompt = st.chat_input("Ask a question about NGL Strategy...", key="chat_input")
        
        if prompt:
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
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
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})
        
        # Clear chat button
        if st.session_state.messages:
            if st.button("🗑️ Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
