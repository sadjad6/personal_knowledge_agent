import streamlit as st
import requests
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json

# Configure the page
st.set_page_config(
    page_title="Personal Knowledge Assistant",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header { font-size: 2.5rem; color: #1f77b4; margin-bottom: 1rem; }
    .sub-header { font-size: 1.5rem; color: #2c3e50; margin: 1.5rem 0 1rem 0; }
    .sidebar .sidebar-content { background-color: #f8f9fa; }
    .stButton>button { width: 100%; margin: 5px 0; }
    .chat-message { padding: 1rem; border-radius: 0.5rem; margin: 0.5rem 0; }
    .user-message { background-color: #e3f2fd; margin-left: 10%; }
    .assistant-message { background-color: #f5f5f5; margin-right: 10%; }
    .summary-card { 
        background-color: #f8f9fa; 
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
    </style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "show_summary" not in st.session_state:
    st.session_state.show_summary = False

# Helper functions
def call_api(endpoint: str, method: str = "get", data: Optional[Dict] = None):
    """Helper function to make API calls."""
    url = f"{API_BASE_URL}/api/v1{endpoint}"
    try:
        if method.lower() == "get":
            response = requests.get(url, params=data)
        elif method.lower() == "post":
            response = requests.post(url, json=data)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# Sidebar
with st.sidebar:
    st.title("🔍 Navigation")
    
    # Navigation
    nav_option = st.radio(
        "Go to",
        ["Chat with Notes", "Recent Updates", "Knowledge Base Status"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick Actions
    st.subheader("Quick Actions")
    if st.button("🔄 Generate Summary Now"):
        with st.spinner("Generating summary..."):
            result = call_api("/summarize", "post")
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Summary generated successfully!")
    
    if st.button("📂 Check for New Notes"):
        with st.spinner("Checking for new notes..."):
            result = call_api("/ingest", "post")
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Notes indexed successfully!")
    
    st.markdown("---")
    
    # System Status
    st.subheader("System Status")
    status = call_api("/status")
    if "error" in status:
        st.error(f"Error: {status['error']}")
    else:
        st.info(f"Status: {status.get('status', 'Unknown')}")
        st.info(f"Vector Store: {status.get('vector_store', 'Unknown')}")
        st.info(f"LLM: {status.get('llm', 'Unknown')}")

# Main content
st.markdown("<h1 class='main-header'>Personal Knowledge Assistant</h1>", unsafe_allow_html=True)

if nav_option == "Chat with Notes":
    # Display chat messages
    st.markdown("<h2 class='sub-header'>Ask about your notes</h2>", unsafe_allow_html=True)
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your notes..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = call_api("/ask", "get", {"q": prompt})
                
                if "error" in response:
                    response_text = f"Error: {response['error']}"
                else:
                    response_text = response.get("answer", "No answer found.")
                
                # Display assistant response
                st.markdown(response_text)
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": response_text})

elif nav_option == "Recent Updates":
    st.markdown("<h2 class='sub-header'>Recent Updates</h2>", unsafe_allow_html=True)
    
    with st.spinner("Loading recent updates..."):
        updates = call_api("/ask", "get", {"q": "Show me recent updates"})
        
        if "error" in updates:
            st.error(f"Error: {updates['error']}")
        else:
            if not updates.get("answer"):
                st.info("No recent updates found.")
            else:
                st.markdown(updates["answer"], unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Manual summary section
    st.markdown("<h3 class='sub-header'>Generate Summary</h3>", unsafe_allow_html=True)
    
    if st.button("📝 Generate Daily Summary"):
        with st.spinner("Generating summary of recent notes..."):
            result = call_api("/summarize", "post")
            if "error" in result:
                st.error(f"Error: {result['error']}")
            else:
                st.success("Summary generated successfully!")
                st.markdown("---")
                st.markdown("### Generated Summary")
                st.markdown(f"<div class='summary-card'>{result.get('summary', 'No content')}</div>", 
                           unsafe_allow_html=True)

else:  # Knowledge Base Status
    st.markdown("<h2 class='sub-header'>Knowledge Base Status</h2>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### System Information")
        status = call_api("/status")
        
        if "error" in status:
            st.error(f"Error: {status['error']}")
        else:
            st.info(f"**Status:** {status.get('status', 'Unknown')}")
            st.info(f"**Vector Store:** {status.get('vector_store', 'Unknown')}")
            st.info(f"**LLM:** {status.get('llm', 'Unknown')}")
            st.info(f"**Notes Directory:** {status.get('notes_dir', 'Unknown')}")
            st.info(f"**Summaries Directory:** {status.get('summaries_dir', 'Unknown')}")
    
    with col2:
        st.markdown("### Actions")
        
        if st.button("🔄 Reindex All Notes"):
            with st.spinner("Reindexing all notes..."):
                result = call_api("/ingest", "post")
                if "error" in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.success("Notes reindexed successfully!")
        
        if st.button("📊 View Collection Stats"):
            with st.spinner("Fetching collection statistics..."):
                stats = call_api("/status")  # This would need a proper stats endpoint
                if "error" in stats:
                    st.error(f"Error: {stats['error']}")
                else:
                    st.json(stats)
    
    st.markdown("---")
    st.markdown("### Recent Summaries")
    
    # This would need to be implemented with actual file system access
    st.info("Recent summaries will appear here. Use the 'Generate Summary' button to create new ones.")

# Add some space at the bottom
st.markdown("<br><br>", unsafe_allow_html=True)
