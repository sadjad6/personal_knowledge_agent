import pytest
from fastapi import status
from unittest.mock import patch, MagicMock

class TestAPIEndpoints:
    """Test cases for the API endpoints."""
    
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "healthy"}
    
    @patch('backend.services.qa.get_qa_response')
    def test_ask_endpoint(self, mock_qa, client):
        """Test the ask endpoint."""
        # Mock the QA response
        mock_qa.return_value = "This is a test answer."
        
        # Make the request
        response = client.get("/api/v1/ask?q=test+question")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"question": "test question", "answer": "This is a test answer."}
        mock_qa.assert_called_once_with("test question", limit=5)
    
    @patch('backend.services.summarizer.generate_daily_summary')
    def test_summarize_endpoint(self, mock_summary, client):
        """Test the summarize endpoint."""
        # Mock the summary response
        test_summary = "This is a test summary."
        mock_summary.return_value = test_summary
        
        # Make the request
        response = client.post("/api/v1/summarize")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "success", "summary": test_summary}
        mock_summary.assert_called_once()
    
    @patch('backend.rag.indexer.VectorIndexer')
    def test_status_endpoint(self, mock_indexer, client):
        """Test the status endpoint."""
        # Mock the indexer response
        mock_instance = MagicMock()
        mock_instance.get_collection_info.return_value = {
            "name": "test_collection",
            "status": "green",
            "vectors_count": 100,
            "points_count": 100
        }
        mock_indexer.return_value = mock_instance
        
        # Make the request
        response = client.get("/api/v1/status")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "operational"
        assert data["vector_store"] == "Qdrant"
        assert "llm" in data
        assert "notes_dir" in data
        assert "summaries_dir" in data
    
    @patch('backend.services.loader.load_documents')
    @patch('backend.rag.indexer.VectorIndexer')
    def test_ingest_endpoint(self, mock_indexer, mock_loader, client):
        """Test the ingest endpoint."""
        # Mock the loader and indexer
        test_docs = [{"content": "Test doc", "metadata": {"source": "test.md"}}]
        mock_loader.return_value = test_docs
        mock_instance = MagicMock()
        mock_instance.index_documents.return_value = len(test_docs)
        mock_indexer.return_value = mock_instance
        
        # Make the request
        response = client.post("/api/v1/ingest")
        
        # Assertions
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"status": "ingestion started"}
        mock_loader.assert_called_once()
        mock_instance.index_documents.assert_called_once()
