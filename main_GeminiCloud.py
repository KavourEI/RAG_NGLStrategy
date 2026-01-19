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

# Clean CSS
st.markdown("""
<style>
    /* Base reset */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden !important;
    }

    /* Main app container */
    .stApp {
        background-color: #343541 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        font-size: 14px !important;
        line-height: 1.5 !important;
    }

    /* Fix font sizes */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        font-size: 14px !important;
        line-height: 1.5 !important;
    }

    /* Fix chat messages */
    .stChatMessage {
        padding: 12px 0 !important;
        margin: 0 !important;
    }

    .stChatMessage div {
        font-size: 14px !important;
        line-height: 1.5 !important;
    }

    /* Fix code block styling that might be interfering */
    code, pre {
        background-color: transparent !important;
        border: none !important;
        padding: 0 !important;
        font-size: 14px !important;
        font-family: inherit !important;
        white-space: pre-wrap !important;
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


            def fix_markdown_formatting(text):
                """
                Fix the specific issue where text is formatted with each character on a new line.
                This happens when LLM tries to create subscript/superscript or code blocks.
                """
                if not text:
                    return ""

                # Pattern 1: Fix text where each character is on a new line
                # Example: "6\n3\n9\n−\n6\n4\n9\n/\nm\nt"
                lines = text.split('\n')

                # If we have many single-character lines in sequence, join them
                i = 0
                result_lines = []

                while i < len(lines):
                    current_line = lines[i].strip()

                    # Check if this line is a single character (or very short)
                    # and if there's a sequence of similar lines
                    if len(current_line) <= 2 and i < len(lines) - 1:
                        # Look ahead to see if we have a sequence of short lines
                        sequence = [current_line]
                        j = i + 1

                        while j < len(lines) and len(lines[j].strip()) <= 2:
                            sequence.append(lines[j].strip())
                            j += 1

                        # If we found a sequence of at least 3 short lines, join them
                        if len(sequence) >= 3:
                            joined = ''.join(sequence)
                            result_lines.append(joined)
                            i = j
                            continue

                    result_lines.append(current_line)
                    i += 1

                text = '\n'.join(result_lines)

                # Pattern 2: Fix specific patterns like "639−649/mtforsecond−halfJulydeliveryand"
                # This happens when spaces are removed between words and numbers

                # Add spaces between words and numbers
                text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)
                text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)

                # Fix common price patterns
                text = re.sub(r'(\d+)[−‑–—](\d+)/mt', r'\1-\2/mt', text)
                text = re.sub(r'\$(\d+)/mt', r'$\1/mt', text)
                text = re.sub(r'(\d+)-(\d+)/mt', r'\1-\2/mt', text)

                # Fix common phrases
                text = re.sub(r'second-half', 'second-half', text)
                text = re.sub(r'first-half', 'first-half', text)

                # Fix abbreviations
                text = re.sub(r'\bC\s*F\s*R\b', 'CFR', text)
                text = re.sub(r'\bF\s*O\s*B\b', 'FOB', text)
                text = re.sub(r'\bm\s*t\b', 'mt', text)
                text = re.sub(r'\bC\s*P\b', 'CP', text)

                # Fix spaces after punctuation
                text = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', text)

                # Fix specific problematic patterns from your example
                patterns = [
                    (r'639−649/mtforsecond−halfJulydeliveryand', '639-649/mt for second-half July delivery and'),
                    (r'85−95/mttotherespectiveJulyandAugustContractPrices',
                     '85-95/mt to the respective July and August Contract Prices'),
                    (r'second−halfof2025', 'second-half of 2025'),
                    (r'\$80/mtto\$90/mt', '$80/mt to $90/mt'),
                    (r'48−50/mt', '48-50/mt'),
                    (r'\$45to\$50/mt', '$45 to $50/mt'),
                    (r'\$57and\$58', '$57 and $58'),
                ]

                for pattern, replacement in patterns:
                    text = text.replace(pattern, replacement)

                # Final cleanup of multiple spaces
                text = re.sub(r'\s+', ' ', text)
                text = re.sub(r'\n\s*\n+', '\n\n', text)

                return text.strip()


            def clean_llm_response(text):
                """Main cleaning function for LLM responses"""
                if not text:
                    return ""

                # First pass: Fix markdown formatting issues
                text = fix_markdown_formatting(text)

                # Second pass: General cleanup
                text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)  # Add space between lower and uppercase
                text = re.sub(r'([A-Za-z])\.([A-Z])', r'\1. \2', text)  # Add space after period before capital

                # Fix price ranges
                text = re.sub(r'(\d)\s*-\s*(\d)', r'\1-\2', text)

                # Remove any remaining single-character lines
                lines = text.split('\n')
                cleaned_lines = []
                for line in lines:
                    line = line.strip()
                    if line and len(line) > 1:  # Skip single character lines
                        cleaned_lines.append(line)

                text = ' '.join(cleaned_lines)

                return text


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

        # New helper: render messages with a name label instead of an emoji avatar
        def render_message(message):
            role = message.get("role", "")
            content = message.get("content", "") or ""
            # Determine display name
            if role == "user":
                name = st.session_state.get("username") or "User"
            elif role == "assistant":
                name = "Bot"
            else:
                # fallback for any other role
                name = role.capitalize() or "User"
            # Display the speaker name and the content. Minimal formatting to look like chat.
            st.markdown(f"**{name}**")
            # Keep the original content formatting (avoid code block auto-formatting)
            st.markdown(content)

        # Display chat messages (use the helper, do not use st.chat_message to avoid emojis)
        for message in st.session_state.messages:
            render_message(message)

        # Chat input
        prompt = st.chat_input("Ask a question about NGL Strategy...", key="chat_input")

        if prompt:
            # Add user message to history and render it using the helper
            st.session_state.messages.append({"role": "user", "content": prompt})
            render_message({"role": "user", "content": prompt})

            # Get AI response
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

                    # Clean the response
                    cleaned_response = clean_llm_response(response_text)

                    # Render assistant message using the helper (shows "Bot" as speaker)
                    render_message({"role": "assistant", "content": cleaned_response})
                    st.session_state.messages.append({"role": "assistant", "content": cleaned_response})

                except Exception as e:
                    error_msg = f"Error: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
                    render_message({"role": "assistant", "content": error_msg})

        # Clear chat button
        if st.session_state.messages:
            if st.button("Clear Chat History", type="secondary"):
                st.session_state.messages = []
                st.rerun()
