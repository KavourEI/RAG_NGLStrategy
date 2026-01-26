import streamlit as st

def render():
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
