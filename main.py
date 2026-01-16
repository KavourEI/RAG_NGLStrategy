import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st

def get_secret(key):
    """Get secret from Streamlit secrets or environment variables"""
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return os.getenv(key)

# Configure the page
st.set_page_config(
    page_title="NGL Strategy RAG Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for ChatGPT-like appearance
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Söhne:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main background - ChatGPT dark theme */
    .stApp {
        background-color: #343541 !important;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        max-width: 67.2rem !important;
        background-color: #343541 !important;
    }
    
    /* Sidebar - ChatGPT style */
    [data-testid="stSidebar"] {
        background-color: #202123 !important;
        border-right: 1px solid #2f2f2f !important;
    }
    
    [data-testid="stSidebar"] * {
        color: #ececf1 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Sidebar headers */
    [data-testid="stSidebar"] h1 {
        color: #ececf1 !important;
        font-size: 1.25rem !important;
        font-weight: 600 !important;
        padding: 0.5rem 0 !important;
    }
    
    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        transition: all 0.2s !important;
        width: 100% !important;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #2a2b32 !important;
        border-color: #8e8ea0 !important;
    }
    
    /* Sidebar text inputs */
    [data-testid="stSidebar"] input {
        background-color: #40414f !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        border-radius: 6px !important;
        padding: 0.75rem !important;
    }
    
    [data-testid="stSidebar"] input:focus {
        border-color: #8e8ea0 !important;
        box-shadow: 0 0 0 1px #8e8ea0 !important;
    }
    
    /* Radio buttons in sidebar */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem !important;
    }
    
    [data-testid="stSidebar"] .stRadio label {
        background-color: transparent !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.2s !important;
    }
    
    [data-testid="stSidebar"] .stRadio label:hover {
        background-color: #2a2b32 !important;
    }
    
    /* Success/error messages in sidebar */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stError {
        background-color: #2a2b32 !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        font-size: 0.875rem !important;
    }
    
    /* All text color */
    html, body, [class*="css"], p, div, span, label {
        color: #ececf1 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Headers - ChatGPT style */
    h1, h2, h3 {
        color: #ececf1 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
        font-weight: 600 !important;
    }
    
    h1 {
        font-size: 2rem !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 1.5rem !important;
    }
    
    h3 {
        font-size: 1.25rem !important;
    }
    
    /* Chat messages - ChatGPT style */
    .stChatMessage {
        background-color: transparent !important;
        padding: 1.5rem 0 !important;
        border-radius: 0 !important;
    }
    
    /* User messages */
    .stChatMessage[data-testid*="user"] {
        background-color: #343541 !important;
    }
    
    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] {
        background-color: #444654 !important;
        border-top: 1px solid rgba(255,255,255,0.1) !important;
        border-bottom: 1px solid rgba(255,255,255,0.1) !important;
    }
    
    /* Chat message content */
    .stChatMessage div {
        color: #ececf1 !important;
        font-size: 16px !important;
        line-height: 1.75 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Chat input */
    .stChatInputContainer {
        background-color: #343541 !important;
        border-top: 1px solid #2f2f2f !important;
        padding: 1rem 0 !important;
    }
    
    /* Chat floating input container - controls the bottom input area */
    .stChatFloatingInputContainer,
    [data-testid="stChatFloatingInputContainer"] {
        background-color: transparent !important;
        border-top: 1px solid #2f2f2f !important;
        padding: 1rem !important;
    }
    
    .stChatInput {
        background-color: #40414f !important;
        border: 1px solid #ffffff !important;
        border-radius: 12px !important;
        color: #ececf1 !important;
        padding: 0.75rem 1rem !important;
        font-size: 16px !important;
    }
    
    .stChatInput:focus {
        border-color: #ffffff !important;
        box-shadow: 0 0 0 1px #ffffff !important;
        outline: none !important;
    }
    
    /* Buttons - ChatGPT style */
    .stButton button {
        background-color: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        transition: all 0.2s !important;
    }
    
    .stButton button:hover {
        background-color: #1a7f64 !important;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #444654 !important;
        border-left: 4px solid #10a37f !important;
        color: #ececf1 !important;
        border-radius: 4px !important;
    }
    
    /* Markdown content on intro page */
    .stMarkdown {
        color: #ececf1 !important;
    }
    
    .stMarkdown li {
        color: #ececf1 !important;
        margin: 0.5rem 0 !important;
    }
    
    /* Links */
    a {
        color: #10a37f !important;
    }
    
    a:hover {
        color: #1a7f64 !important;
    }
    
    /* Divider */
    hr {
        border-color: #2f2f2f !important;
        margin: 2rem 0 !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px !important;
        height: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: #343541 !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #565869 !important;
        border-radius: 4px !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6e6e80 !important;
    }
    
    /* Code blocks */
    code {
        background-color: #2d2d2d !important;
        color: #ececf1 !important;
        padding: 0.2rem 0.4rem !important;
        border-radius: 4px !important;
        font-family: 'Söhne Mono', Monaco, 'Andale Mono', 'Ubuntu Mono', monospace !important;
        font-size: 0.875rem !important;
    }
    
    pre {
        background-color: #2d2d2d !important;
        border-radius: 8px !important;
        padding: 1rem !important;
        overflow-x: auto !important;
    }
    
    /* Chat input placeholder text - white */
    .stChatInput input::placeholder,
    .stChatInput textarea::placeholder,
    [data-testid="stChatInput"] input::placeholder,
    [data-testid="stChatInput"] textarea::placeholder,
    [data-testid="stChatInputTextArea"] textarea::placeholder,
    .stChatInputContainer textarea::placeholder,
    [data-testid="stChatInputContainer"] textarea::placeholder,
    .stChatFloatingInputContainer textarea::placeholder,
    [data-testid="stChatFloatingInputContainer"] textarea::placeholder,
    [data-baseweb="textarea"] textarea::placeholder,
    div[data-testid="stChatInput"] textarea::placeholder {
        color: white !important;
        opacity: 1 !important;
        -webkit-text-fill-color: white !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Sidebar navigation and login
with st.sidebar:
    st.title("NGL Strategy")

    if not st.session_state.authenticated:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Simple authentication - you can replace this with your own logic
            if username and password:  # Accept any non-empty credentials for demo
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"Welcome, {username}!")
                st.rerun()
            else:
                st.error("Please enter username and password")
    else:
        st.success(f"Logged in as: {st.session_state.username}")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = ""
            st.rerun()

        st.divider()

        # Navigation
        page = st.radio(
            "Navigation",
            ["Chat", "About"],
            label_visibility="visible"
        )

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to NGL Strategy Assistant")
    st.markdown("### Please login to continue")

    st.markdown("""
    
    This AI assistant helps you explore and understand NGL Strategy documents through natural conversation.
    
    **Features:**
    - 💬 Natural language queries
    - 📚 Knowledge base powered by your documents
    - 🎯 Accurate, contextual responses
    
    Login using the sidebar to get started.
    """)
else:
    # Show selected page
    if page == "About":
        # Introduction Page - ChatGPT style
        st.title("NGL Strategy Assistant")

        st.markdown("""
        ### Welcome to your AI-powered NGL Strategy assistant
        
        This assistant uses advanced AI to help you understand and analyze NGL (Natural Gas Liquids) 
        strategy documents. Ask questions and get instant, accurate answers based on your organization's 
        knowledge base.
        
        ---
        
        #### How it works
        
        **Document Understanding**  
        Your documents are indexed and processed to enable intelligent search and retrieval of relevant information.
        
        **Context-Aware Responses**  
        The AI analyzes your question along with relevant document sections to provide accurate, contextual answers.
        
        **Natural Conversation**  
        Chat naturally with your knowledge base - ask follow-up questions and explore topics in depth.
        
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
        - **Ollama (gpt-oss:120b)** for natural language understanding
        - **LlamaIndex** for RAG orchestration
        
        ---
        
        **Ready to start?** Navigate to the Chat page to begin asking questions.
        """)

    elif page == "Chat":
        # Import here to avoid loading if not needed
        from llama_cloud_services import LlamaCloudIndex
        from llama_index.llms.ollama import Ollama
        import re

        def clean_text(text):
            """Comprehensive text cleaning to fix OCR and formatting issues"""
            # Remove asterisks used for emphasis
            text = re.sub(r'\*+', '', text)

            # Fix severely spaced-out text (e.g., "6 3 9" -> "639", "/ m t" -> "/mt")
            # This handles when each character is separated by spaces
            # Match sequences like: "6 3 9 - 6 4 9" and remove the spaces
            text = re.sub(r'(\d)\s+(?=\d)', r'\1', text)  # Fix spaced numbers
            text = re.sub(r'([/$])\s+', r'\1', text)  # Fix "/ " or "$ "
            text = re.sub(r'\s+([/$])', r'\1', text)  # Fix " /" or " $"

            # Fix common unit patterns
            text = re.sub(r'/\s*m\s*t\b', '/mt', text, flags=re.IGNORECASE)
            text = re.sub(r'U\s*S\s*\$?\s*', 'US$', text)
            text = re.sub(r'\$\s+(\d)', r'$\1', text)

            # Fix spaced letters in common words (be careful not to break actual words)
            # Pattern: single char followed by space and another single char (repeated)
            # Example: "c a r r y i n g" -> "carrying"
            # Only do this for lowercase sequences of 3+ chars
            def fix_spaced_word(match):
                return match.group(0).replace(' ', '')

            text = re.sub(r'\b([a-z])\s+([a-z])\s+([a-z](?:\s+[a-z])*)\b', fix_spaced_word, text, flags=re.IGNORECASE)

            # Normalize multiple spaces to single space
            text = re.sub(r' +', ' ', text)

            # Normalize line breaks - max 2 newlines (one blank line)
            text = re.sub(r'\n\s*\n+', '\n\n', text)

            # Clean up extra whitespace around punctuation
            text = re.sub(r'\s+([,;:.!?)])', r'\1', text)
            text = re.sub(r'([(])\s+', r'\1', text)
            text = re.sub(r'([,;:.!?])\s+', r'\1 ', text)

            # Fix common number-dash patterns (e.g., "639 - 649" -> "639-649")
            text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', text)

            return text.strip()

        # Cache the resources
        @st.cache_resource
        def get_index():
            LLAMACLOUD_API_KEY = get_secret('LLAMA_CLOUD_API_KEY')
            LLAMACLOUD_ORG_ID = get_secret('LLAMA_ORG_ID')

            return LlamaCloudIndex(
                name="NGL_Strategy",
                project_name="Default",
                organization_id=LLAMACLOUD_ORG_ID,
                api_key=LLAMACLOUD_API_KEY
            )

        @st.cache_resource
        def get_llm():
            return Ollama(
                model="gpt-oss:120b",
                base_url="https://ollama.com",
                request_timeout=120.0,
                additional_kwargs={
                    'headers': {
                        'Authorization': f'Bearer {get_secret("OLLAMA_API_KEY")}'
                    }
                }
            )

        @st.cache_resource
        def get_query_engine():
            index = get_index()
            llm = get_llm()
            return index.as_query_engine(llm=llm)

        # Chatbot Page
        st.title("Chat")

        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
            # Add greeting message when user first enters chat
            greeting = f"Hello{', ' + st.session_state.username if st.session_state.username else ''}! 👋 I'm your NGL Strategy Assistant. How can I help you today? Feel free to ask me any questions about documents that are already submited... for now!"
            st.session_state.messages.append({"role": "assistant", "content": greeting})

        # Display chat history
        for i, message in enumerate(st.session_state.messages):
            avatar = "🤖" if message["role"] == "assistant" else "👤"
            with st.chat_message(message["role"], avatar=avatar):
                # Clean up the message content
                clean_content = clean_text(message["content"])
                # Display with ChatGPT styling
                st.markdown(clean_content)

        # Chat input
        if prompt := st.chat_input("Ask a question about NGL Strategy..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})

            # Display user message
            with st.chat_message("user", avatar="👤"):
                st.markdown(prompt)

            # Generate response
            with st.chat_message("assistant", avatar="🤖"):
                with st.spinner("Thinking..."):
                    try:
                        engine = get_query_engine()
                        response = engine.query(prompt)

                        # Try to get the response text properly
                        if hasattr(response, 'response'):
                            response_text = response.response
                        elif hasattr(response, 'text'):
                            response_text = response.text
                        else:
                            response_text = str(response)

                        # Clean the response text using comprehensive cleaning function
                        response_text = clean_text(response_text)

                        # Display with ChatGPT styling
                        st.markdown(response_text)

                        # Add assistant response to chat history
                        st.session_state.messages.append({"role": "assistant", "content": response_text})

                    except Exception as e:
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        # Clear chat button
        if st.session_state.messages:
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
