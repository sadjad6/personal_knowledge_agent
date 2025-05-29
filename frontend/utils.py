import os
import json
from typing import Dict, Any, List, Optional
import requests

# Get API base URL from environment or use default
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

def call_api(
    endpoint: str, 
    method: str = "get", 
    data: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Make an API call to the backend.
    
    Args:
        endpoint: API endpoint (e.g., '/ask')
        method: HTTP method ('get' or 'post')
        data: JSON data for POST requests
        params: Query parameters for GET requests
        
    Returns:
        Dictionary with the API response or error
    """
    url = f"{API_BASE_URL}/api/v1{endpoint}"
    headers = {"Content-Type": "application/json"}
    
    try:
        if method.lower() == "get":
            response = requests.get(url, params=params, headers=headers, timeout=30)
        elif method.lower() == "post":
            response = requests.post(url, json=data, headers=headers, timeout=30)
        else:
            return {"error": f"Unsupported method: {method}"}
        
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def format_chat_message(role: str, content: str) -> Dict[str, str]:
    """Format a chat message for the UI."""
    return {"role": role, "content": content}

def get_recent_updates(days: int = 7) -> List[Dict[str, Any]]:
    """Get recently updated notes."""
    result = call_api("/ask", "get", params={"q": f"Show me updates from the last {days} days"})
    return result.get("answer", [])

def generate_summary() -> Dict[str, Any]:
    """Trigger summary generation."""
    return call_api("/summarize", "post")

def ask_question(question: str) -> Dict[str, Any]:
    """Send a question to the QA system."""
    return call_api("/ask", "get", params={"q": question})

def get_system_status() -> Dict[str, Any]:
    """Get system status information."""
    return call_api("/status")

def reindex_notes() -> Dict[str, Any]:
    """Trigger reindexing of all notes."""
    return call_api("/ingest", "post")
