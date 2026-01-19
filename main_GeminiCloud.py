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

# Custom CSS for ChatGPT-like appearance
st.markdown("""
<style>
    :root{
        /* dynamic vars set from JS on load/resize */
        --sidebar-width: 336px; /* fallback */
        --content-max-width: 1075px; /* fallback */
        --bottom-padding: 150px; /* fallback */
        --base-font-size: 16px; /* fallback */
        --is-mobile: 0;
    }

    @import url('https://fonts.googleapis.com/css2?family=Söhne:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Main background - ChatGPT dark theme */
    .stApp {
        background-color: #343541 !important;
        font-size: var(--base-font-size) !important;
        -webkit-tap-highlight-color: rgba(0,0,0,0);
    }

    /* Main content area */
    .main .block-container {
        padding-top: calc(var(--base-font-size) * 1.25) !important;
        padding-bottom: var(--bottom-padding) !important;
        max-width: var(--content-max-width) !important;
        background-color: #343541 !important;
        /* ensure content area leaves room for fixed bottom input */
        max-height: calc(100vh - var(--bottom-padding)) !important;
        overflow-y: auto !important;
        margin-left: 0 auto !important;
    }

    /* Sidebar - ChatGPT style */
    [data-testid="stSidebar"] {
        background-color: #202123 !important;
        border-right: 1px solid #2f2f2f !important;
        width: var(--sidebar-width) !important;
        min-width: 180px !important;
    }

    /* Include emoji-capable fonts in the stack so emoji use system color fonts */
    [data-testid="stSidebar"] *,
    html, body, [class*="css"], p, div, span, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Segoe UI Emoji', 'Noto Color Emoji', 'Apple Color Emoji', sans-serif !important;
        color: #ececf1 !important;
    }

    /* Sidebar specific scaling */
    [data-testid="stSidebar"] * {
        font-size: calc(var(--base-font-size) * 0.95) !important;
    }

    /* Sidebar headers */
    [data-testid="stSidebar"] h1 {
        color: #ececf1 !important;
        font-size: calc(var(--base-font-size) * 1.1) !important;
        font-weight: 600 !important;
        padding: 0.5rem 0 !important;
    }

    /* Sidebar buttons */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        border: 1px solid #565869 !important;
        color: #ececf1 !important;
        border-radius: 6px !important;
        padding: 0.65rem 1rem !important;
        font-size: calc(var(--base-font-size) * 0.95) !important;
        transition: all 0.15s !important;
        width: 100% !important;
        box-sizing: border-box !important;
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
        font-size: calc(var(--base-font-size) * 0.95) !important;
    }

    [data-testid="stSidebar"] input:focus {
        border-color: #8e8ea0 !important;
        box-shadow: 0 0 0 1px #8e8ea0 !important;
    }

    /* Radio & other controls */
    [data-testid="stSidebar"] .stRadio > div {
        gap: 0.5rem !important;
    }

    [data-testid="stSidebar"] .stRadio label {
        background-color: transparent !important;
        padding: 0.5rem 1rem !important;
        border-radius: 6px !important;
        cursor: pointer !important;
        transition: all 0.15s !important;
        font-size: calc(var(--base-font-size) * 0.95) !important;
    }

    /* Success/error messages in sidebar */
    [data-testid="stSidebar"] .stSuccess,
    [data-testid="stSidebar"] .stError {
        background-color: #2a2b32 !important;
        border-radius: 6px !important;
        padding: 0.5rem !important;
        font-size: 0.95rem !important;
    }

    /* Headers - scaled */
    h1, h2, h3 {
        color: #ececf1 !important;
        font-weight: 600 !important;
    }

    h1 { font-size: calc(var(--base-font-size) * 1.75) !important; margin-bottom: 1rem !important; }
    h2 { font-size: calc(var(--base-font-size) * 1.35) !important; }
    h3 { font-size: calc(var(--base-font-size) * 1.1) !important; }

    /* Chat messages - ChatGPT style */
    .stChatMessage {
        background-color: transparent !important;
        padding: calc(var(--base-font-size) * 1) 0 !important;
        border-radius: 0 !important;
    }

    /* Assistant messages */
    .stChatMessage[data-testid*="assistant"] {
        background-color: #444654 !important;
        border-top: 1px solid rgba(255,255,255,0.08) !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
    }

    /* Chat message content */
    .stChatMessage div {
        color: #ececf1 !important;
        font-size: calc(var(--base-font-size) * 1) !important;
        line-height: 1.6 !important;
    }

    /* Chat input container and fixed bottom area use dynamic sidebar width for left offset */
    [data-testid="stBottom"] {
        position: fixed !important;
        bottom: 0 !important;
        left: var(--sidebar-width) !important;
        right: 0 !important;
        background-color: #343541 !important;
        padding: calc(var(--base-font-size) * 0.75) !important;
        z-index: 1000 !important;
        border-top: 1px solid #2f2f2f !important;
        box-sizing: border-box !important;
    }

    .stChatFloatingInputContainer,
    [data-testid="stChatFloatingInputContainer"] {
        background-color: transparent !important;
        border-top: 1px solid #2f2f2f !important;
        padding: calc(var(--base-font-size) * 0.75) !important;
        position: fixed !important;
        bottom: 0 !important;
        left: var(--sidebar-width) !important;
        right: 0 !important;
        z-index: 1000 !important;
        box-sizing: border-box !important;
    }

    /* When sidebar is collapsed (desktop toggle) */
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main [data-testid="stBottom"],
    [data-testid="stSidebar"][aria-expanded="false"] ~ .main .stChatFloatingInputContainer {
        left: 0 !important;
    }

    /* Center the chat input content */
    [data-testid="stBottom"] > div,
    .stChatFloatingInputContainer > div {
        max-width: var(--content-max-width) !important;
        margin: 0 auto !important;
    }

    /* Add padding at bottom of main content to prevent overlap with fixed input (uses dynamic var) */
    .main .block-container {
        padding-bottom: var(--bottom-padding) !important;
    }

    /* Make chat messages container scrollable and responsive */
    [data-testid="stChatMessageContainer"] {
        max-height: calc(100vh - var(--bottom-padding) - 30px) !important;
        overflow-y: auto !important;
        padding-bottom: calc(var(--base-font-size) * 1.25) !important;
        -webkit-overflow-scrolling: touch !important;
    }

    /* Chat input full width behavior */
    .stChatInput, .stChatInput textarea, .stChatInput input, [data-testid="stChatInput"] textarea {
        font-size: calc(var(--base-font-size) * 1) !important;
        background-color: #40414f !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        color: #ececf1 !important;
        border-radius: 12px !important;
        padding: 0.75rem 1rem !important;
        box-sizing: border-box !important;
        width: 100% !important;
    }

    /* Buttons - touch friendly */
    .stButton button {
        padding: 0.65rem 1rem !important;
        border-radius: 8px !important;
        font-size: calc(var(--base-font-size) * 0.98) !important;
    }

    /* Code blocks scale */
    code { font-size: calc(var(--base-font-size) * 0.9) !important; }
    pre { font-size: calc(var(--base-font-size) * 0.9) !important; }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* MOBILE SPECIFIC: fallback adjustments for narrow viewports */
    @media (max-width: 760px) {
        :root { --is-mobile: 1; }
        /* Force sidebar off-canvas visually */
        [data-testid="stSidebar"] {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            height: 100vh !important;
            transform: translateX(-110%) !important;
            z-index: 1300 !important;
            transition: transform 240ms ease-in-out !important;
            width: calc(var(--sidebar-width)) !important;
            box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
        }

        /* When the class is set on the root, reveal the sidebar */
        .mobile-sidebar-open [data-testid="stSidebar"] {
            transform: translateX(0) !important;
        }

        /* overlay shown when sidebar open */
        #mobile-sidebar-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0,0,0,0.45);
            z-index: 1290;
            transition: opacity 180ms ease-in-out;
        }
        .mobile-sidebar-open #mobile-sidebar-overlay {
            display: block;
            opacity: 1;
        }

        /* toggle button */
        #mobile-sidebar-toggle {
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 1310;
            background: rgba(20,20,20,0.85);
            color: #fff;
            border: 1px solid rgba(255,255,255,0.06);
            padding: 8px 10px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: calc(var(--base-font-size) * 1.0);
            cursor: pointer;
            -webkit-tap-highlight-color: transparent;
            box-shadow: 0 6px 18px rgba(0,0,0,0.4);
        }

        /* when sidebar is open, prevent page from being scrolled */
        .mobile-sidebar-open body, .mobile-sidebar-open html {
            overflow: hidden !important;
            touch-action: none !important;
        }

        /* Content should be full width */
        .main .block-container { max-width: 100% !important; padding-left: 12px !important; padding-right: 12px !important; }
        /* Make bottom input use full width and sit above the safe area */
        [data-testid="stBottom"], .stChatFloatingInputContainer { left: 0 !important; right: 0 !important; padding-left: 12px !important; padding-right: 12px !important; }
        /* Increase touch target sizes */
        [data-testid="stSidebar"] .stButton button { padding: 0.9rem 1rem !important; font-size: calc(var(--base-font-size) * 1.05) !important; }
        /* reduce message padding on small screens */
        .stChatMessage { padding: calc(var(--base-font-size) * 0.6) 0 !important; }
        [data-testid="stChatMessageContainer"] { max-height: calc(100vh - var(--bottom-padding) - 20px) !important; }
    }
</style>

<script>
(function(){
  function setSizes(){
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    const vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
    const isMobile = vw <= 760 || Math.max(vh, vw) < 700;

    // sidebar: between 200px and 450px, ~20% of width (desktop). Mobile -> 0
    let sidebarPx = Math.min(Math.max(Math.round(vw * 0.20), 200), 450);
    // content max width: between 540px and 1075px, up to 90% of viewport
    let contentPx = Math.min(Math.max(Math.round(vw * 0.90), 540), 1075);
    // bottom padding: between 100px and 220px, ~18% of viewport height
    let bottomPx = Math.min(Math.max(Math.round(vh * 0.18), 100), 220);
    // base font size: scale with viewport width, clamp 12-18px
    let baseFont = Math.min(Math.max(Math.round(vw * 0.012 + 8), 12), 18);

    if(isMobile){
      sidebarPx = 280; // default overlay width on mobile
      // content should use almost full viewport width with small horizontal margins
      contentPx = Math.max(vw - 24, 320);
      // smaller bottom padding so input doesn't consume too much space
      bottomPx = Math.min(Math.max(Math.round(vh * 0.14), 88), 160);
      // slightly larger font on some phones for readability, but clamp
      baseFont = Math.min(Math.max(Math.round(vw * 0.02 + 10), 13), 18);
      document.documentElement.style.setProperty('--is-mobile', '1');
    } else {
      document.documentElement.style.setProperty('--is-mobile', '0');
    }

    document.documentElement.style.setProperty('--sidebar-width', sidebarPx + 'px');
    document.documentElement.style.setProperty('--content-max-width', contentPx + 'px');
    document.documentElement.style.setProperty('--bottom-padding', bottomPx + 'px');
    document.documentElement.style.setProperty('--base-font-size', baseFont + 'px');
    // also set a --vh unit for any future use
    document.documentElement.style.setProperty('--vh', (vh * 0.01) + 'px');
  }

  // initial set and on-resize update (debounced)
  let resizeTimer = null;
  function updateSizesDebounced(){
    if(resizeTimer) clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => { setSizes(); resizeTimer = null; }, 80);
  }

  setSizes();
  window.addEventListener('resize', updateSizesDebounced);
  // handle orientation change (mobile devices)
  window.addEventListener('orientationchange', function(){ setTimeout(setSizes, 120); });

  /* MOBILE SIDEBAR TOGGLE INJECTION */
  function ensureMobileControls(){
    if(document.getElementById('mobile-sidebar-toggle')) return;

    // create overlay
    const overlay = document.createElement('div');
    overlay.id = 'mobile-sidebar-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    document.body.appendChild(overlay);

    // create toggle button (hamburger)
    const btn = document.createElement('button');
    btn.id = 'mobile-sidebar-toggle';
    btn.type = 'button';
    btn.title = 'Show sidebar';
    btn.innerHTML = '☰ <span style="font-weight:600;margin-left:6px">Menu</span>';
    btn.setAttribute('aria-expanded', 'false');
    btn.setAttribute('aria-controls', 'stSidebar');
    document.body.appendChild(btn);

    function openSidebar(){
      document.documentElement.classList.add('mobile-sidebar-open');
      btn.setAttribute('aria-expanded', 'true');
    }
    function closeSidebar(){
      document.documentElement.classList.remove('mobile-sidebar-open');
      btn.setAttribute('aria-expanded', 'false');
    }

    btn.addEventListener('click', function(e){
      e.stopPropagation();
      if(document.documentElement.classList.contains('mobile-sidebar-open')) closeSidebar();
      else openSidebar();
    });

    overlay.addEventListener('click', function(){ closeSidebar(); });

    // close on escape
    window.addEventListener('keydown', function(ev){
      if(ev.key === 'Escape') closeSidebar();
    });

    // tap outside sidebar closes it (detect clicks outside)
    document.addEventListener('click', function(e){
      if(!document.documentElement.classList.contains('mobile-sidebar-open')) return;
      const sidebar = document.querySelector('[data-testid="stSidebar"]');
      if(!sidebar) return;
      if(!sidebar.contains(e.target) && e.target.id !== 'mobile-sidebar-toggle') closeSidebar();
    }, {capture: true});

    // when touch-moving inside sidebar allow scroll, otherwise prevent body scroll
    document.addEventListener('touchstart', function(){}, {passive: true});
  }

  // create controls only for mobile viewport
  function handleMobileControlsVisibility(){
    const vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
    const mobile = vw <= 760;
    if(mobile) ensureMobileControls();
    // hide button on desktop by CSS but leave it in DOM; nothing else required
  }

  handleMobileControlsVisibility();
  window.addEventListener('resize', function(){ updateSizesDebounced(); handleMobileControlsVisibility(); });
})();
</script>
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
            if username and password:
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
    if page == "About":
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

    elif page == "Chat":
        from llama_cloud_services import LlamaCloudIndex
        # CHANGED: Import Gemini instead of Ollama
        from llama_index.llms.gemini import Gemini
        import re


        def clean_text(text):
            """Comprehensive text cleaning to fix OCR and formatting issues"""
            text = re.sub(r'\*+', '', text)
            text = re.sub(r'[−‑–—]', '-', text)
            text = re.sub(r'/\s*m\s*t\b', '/mt', text, flags=re.IGNORECASE)

            def fix_all_spaced_text(text):
                max_iterations = 10
                for _ in range(max_iterations):
                    original = text
                    text = re.sub(
                        r'\b([a-zA-Z]) ((?:[a-zA-Z] ){1,}[a-zA-Z])\b',
                        lambda m: m.group(0).replace(' ', ''),
                        text
                    )
                    text = re.sub(
                        r'\b(\d) ((?:\d ){0,}\d)\b',
                        lambda m: m.group(0).replace(' ', ''),
                        text
                    )
                    if text == original:
                        break
                return text

            text = fix_all_spaced_text(text)
            text = re.sub(r'\$\s+', '$', text)
            text = re.sub(r'\s+\$', ' $', text)
            text = re.sub(r'U\s*S\s*\$', 'US$', text)
            text = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', text)
            text = re.sub(r'\.([A-Z])', r'. \1', text)
            text = re.sub(r' +', ' ', text)
            text = re.sub(r'\n\s*\n+', '\n\n', text)
            text = re.sub(r'\s+([,;:.!?)])', r'\1', text)
            text = re.sub(r'([(])\s+', r'\1', text)
            return text.strip()


        @st.cache_resource
        def get_index():
            LLAMACLOUD_API_KEY = os.getenv('LLAMA_CLOUD_API_KEY')
            LLAMACLOUD_ORG_ID = os.getenv('LLAMA_ORG_ID')

            return LlamaCloudIndex(
                name="NGL_Strategy",
                project_name="Default",
                organization_id=LLAMACLOUD_ORG_ID,
                api_key=LLAMACLOUD_API_KEY
            )


        # CHANGED: Configuration for Gemini
        @st.cache_resource
        def get_llm():
            return Gemini(
                model="models/gemini-2.5-flash",
                api_key=os.getenv("GOOGLE_API_KEY")
            )


        @st.cache_resource
        def get_query_engine():
            index = get_index()
            llm = get_llm()
            return index.as_query_engine(llm=llm)


        st.title("Chat")

        if "messages" not in st.session_state:
            st.session_state.messages = []

        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                clean_content = clean_text(message["content"])
                st.markdown(clean_content)

        if prompt := st.chat_input("Ask a question about NGL Strategy..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

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
                        error_msg = f"❌ Error: {str(e)}"
                        st.error(error_msg)
                        st.session_state.messages.append({"role": "assistant", "content": error_msg})

        if st.session_state.messages:
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
