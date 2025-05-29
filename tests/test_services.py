import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

class TestQAService:
    """Test cases for the QA service."""
    
    @pytest.mark.asyncio
    @patch('backend.services.qa.VectorIndexer')
    @patch('backend.services.qa.ChatOllama')
    async def test_get_qa_response(self, mock_llm, mock_indexer):
        """Test getting a QA response with context."""
        from backend.services.qa import get_qa_response
        
        # Mock the vector indexer
        mock_indexer_instance = MagicMock()
        mock_indexer_instance.similarity_search.return_value = [
            {
                'content': 'Test context',
                'metadata': {'source': 'test.md'},
                'score': 0.9
            }
        ]
        mock_indexer.return_value = mock_indexer_instance
        
        # Mock the LLM response
        mock_llm_instance = MagicMock()
        mock_llm_instance.ainvoke.return_value.content = "Test answer"
        mock_llm.return_value = mock_llm_instance
        
        # Call the function
        response = await get_qa_response("Test question")
        
        # Assertions
        assert "Test answer" in response
        mock_indexer_instance.similarity_search.assert_called_once()
        mock_llm_instance.ainvoke.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('backend.services.qa.VectorIndexer')
    async def test_get_qa_response_no_results(self, mock_indexer):
        """Test getting a QA response when no results are found."""
        from backend.services.qa import get_qa_response
        
        # Mock the vector indexer to return no results
        mock_indexer_instance = MagicMock()
        mock_indexer_instance.similarity_search.return_value = []
        mock_indexer.return_value = mock_indexer_instance
        
        # Call the function
        response = await get_qa_response("Test question")
        
        # Assertions
        assert "I couldn't find any relevant information" in response
        mock_indexer_instance.similarity_search.assert_called_once()

class TestSummarizerService:
    """Test cases for the summarizer service."""
    
    @pytest.mark.asyncio
    @patch('backend.services.summarizer._get_recent_notes')
    @patch('backend.services.summarizer._generate_summary_with_llm')
    @patch('backend.services.summarizer._save_summary')
    async def test_generate_daily_summary(self, mock_save, mock_generate, mock_recent_notes):
        """Test generating a daily summary."""
        from backend.services.summarizer import generate_daily_summary
        
        # Mock the recent notes
        test_notes = [
            {
                'source': 'test1.md',
                'title': 'Test Note 1',
                'content': 'Test content 1',
                'last_modified': '2023-01-01T00:00:00'
            }
        ]
        mock_recent_notes.return_value = test_notes
        
        # Mock the LLM summary
        mock_generate.return_value = "Test summary"
        
        # Call the function
        summary = await generate_daily_summary()
        
        # Assertions
        assert summary == "Test summary"
        mock_recent_notes.assert_called_once_with(days=1)
        mock_generate.assert_called_once()
        mock_save.assert_called_once_with("Test summary")
    
    @pytest.mark.asyncio
    @patch('backend.services.summarizer._get_recent_notes')
    async def test_generate_daily_summary_no_notes(self, mock_recent_notes):
        """Test generating a daily summary with no recent notes."""
        from backend.services.summarizer import generate_daily_summary
        
        # Mock no recent notes
        mock_recent_notes.return_value = []
        
        # Call the function
        summary = await generate_daily_summary()
        
        # Assertions
        assert "No new or updated notes" in summary
        mock_recent_notes.assert_called_once_with(days=1)

class TestLoaderService:
    """Test cases for the document loader service."""
    
    @pytest.mark.asyncio
    @patch('backend.services.loader.Path')
    async def test_load_documents(self, mock_path):
        """Test loading documents from a directory."""
        from backend.services.loader import load_documents, Document
        
        # Mock the directory structure
        mock_dir = MagicMock()
        mock_dir.rglob.return_value = [
            MagicMock(is_file=MagicMock(return_value=True), suffix='.md', name='test1.md'),
            MagicMock(is_file=MagicMock(return_value=True), suffix='.txt', name='test2.txt'),
            MagicMock(is_file=MagicMock(return_value=True), suffix='.py', name='ignore.py'),
        ]
        
        # Mock the Path object
        mock_path.return_value = mock_dir
        mock_path.return_value.exists.return_value = True
        
        # Mock the load_document function
        with patch('backend.services.loader.load_document') as mock_load:
            mock_load.side_effect = [
                Document(content="Test content 1", metadata={"title": "Test 1"}, source_path=Path("test1.md")),
                Document(content="Test content 2", metadata={"title": "Test 2"}, source_path=Path("test2.txt")),
            ]
            
            # Call the function
            docs = load_documents(Path("test_dir"))
            
            # Assertions
            assert len(docs) == 2
            assert docs[0].content == "Test content 1"
            assert docs[1].content == "Test content 2"
            assert mock_load.call_count == 2
