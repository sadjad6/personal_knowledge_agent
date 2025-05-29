import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.main import app
from backend.config import settings

# Configure test settings
settings.TESTING = True
settings.QDRANT_URL = "http://test-qdrant:6333"
settings.OLLAMA_BASE_URL = "http://test-ollama:11434"

@pytest.fixture(scope="module")
def client():
    """Create a test client for the FastAPI application."""
    with TestClient(app) as test_client:
        yield test_client

@pytest.fixture
def mock_qdrant():
    """Mock Qdrant client for testing."""
    with patch('backend.rag.indexer.QdrantClient') as mock_qdrant:
        yield mock_qdrant

@pytest.fixture
def mock_ollama():
    """Mock Ollama client for testing."""
    with patch('backend.services.qa.ChatOllama') as mock_ollama:
        yield mock_ollama

@pytest.fixture
def mock_embeddings():
    """Mock HuggingFace embeddings for testing."""
    with patch('backend.rag.indexer.HuggingFaceEmbeddings') as mock_embeddings:
        yield mock_embeddings

@pytest.fixture
def test_document():
    """Create a test document."""
    return {
        "content": "This is a test document about artificial intelligence.",
        "metadata": {
            "source": "test_document.md",
            "title": "Test Document",
            "last_modified": "2023-01-01T00:00:00"
        }
    }
