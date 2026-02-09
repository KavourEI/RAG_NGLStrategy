import os
import re
from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import importlib

# Configure the page
st.set_page_config(
    page_title="NGL Strategy RIM Documents Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
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

    st.divider()

    if not st.session_state.authenticated:
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")


        if st.button("Login", type="primary", use_container_width=True):
            if username and password:
                st.session_state.authenticated = True
                st.session_state.username = username
                # Clear the uploaded_documents cache to force refresh on next page load
                if "uploaded_documents" in st.session_state:
                    del st.session_state.uploaded_documents
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
    # Dynamically import and render the selected page
    pages_map = {
        "Chat": "pages.rag_rim",
        "About": "pages.about",
    }
    module_name = pages_map.get(st.session_state.page)
    if module_name:
        module = importlib.import_module(module_name)
        # each page exposes a render() function
        module.render()
    else:
        st.error("Unknown page selected")
