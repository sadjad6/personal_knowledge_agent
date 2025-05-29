import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from pathlib import Path
from datetime import datetime

class TestVectorIndexer:
    """Test cases for the VectorIndexer class."""
    
    @pytest.fixture
    def mock_qdrant_client(self):
        with patch('backend.rag.indexer.QdrantClient') as mock_qdrant:
            yield mock_qdrant
    
    @pytest.fixture
    def mock_embeddings(self):
        with patch('backend.rag.indexer.HuggingFaceEmbeddings') as mock_embeddings:
            yield mock_embeddings
    
    @pytest.fixture
    def test_documents(self):
        from backend.services.loader import Document
        return [
            Document(
                content="Test document 1 about artificial intelligence",
                metadata={"source": "test1.md", "title": "AI Document"},
                source_path=Path("test1.md")
            ),
            Document(
                content="Test document 2 about machine learning",
                metadata={"source": "test2.md", "title": "ML Document"},
                source_path=Path("test2.md")
            )
        ]
    
    @pytest.mark.asyncio
    async def test_index_documents(self, mock_qdrant_client, mock_embeddings, test_documents):
        """Test indexing documents into the vector store."""
        from backend.rag.indexer import VectorIndexer
        
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_client.get_collections.return_value.collections = []
        
        # Create the indexer
        indexer = VectorIndexer()
        
        # Mock the vector store
        mock_vector_store = AsyncMock()
        with patch('backend.rag.indexer.Qdrant', return_value=mock_vector_store):
            # Mock the add_documents method
            mock_vector_store.aadd_documents.return_value = ["doc1", "doc2"]
            
            # Call the method
            result = await indexer.index_documents(test_documents)
            
            # Assertions
            assert result == 2
            mock_client.create_collection.assert_called_once()
            mock_vector_store.aadd_documents.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_similarity_search(self, mock_qdrant_client, mock_embeddings):
        """Test performing a similarity search."""
        from backend.rag.indexer import VectorIndexer
        
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        mock_client.get_collections.return_value.collections = [MagicMock(name="test_collection")]
        
        # Create the indexer
        indexer = VectorIndexer()
        
        # Mock the vector store
        mock_vector_store = AsyncMock()
        with patch('backend.rag.indexer.Qdrant', return_value=mock_vector_store):
            # Mock the similarity search
            mock_doc = MagicMock()
            mock_doc.page_content = "Test content"
            mock_doc.metadata = {"source": "test.md", "title": "Test"}
            mock_vector_store.asimilarity_search_with_score.return_value = [
                (mock_doc, 0.9)
            ]
            
            # Call the method
            results = await indexer.similarity_search("test query", k=1)
            
            # Assertions
            assert len(results) == 1
            assert results[0]["content"] == "Test content"
            assert results[0]["metadata"]["source"] == "test.md"
            assert results[0]["score"] == 0.9
            mock_vector_store.asimilarity_search_with_score.assert_awaited_once()
    
    @pytest.mark.asyncio
    async def test_get_collection_info(self, mock_qdrant_client, mock_embeddings):
        """Test getting collection information."""
        from backend.rag.indexer import VectorIndexer
        
        # Mock the Qdrant client
        mock_client = MagicMock()
        mock_qdrant_client.return_value = mock_client
        
        # Mock the collection info
        mock_collection = MagicMock()
        mock_collection.name = "test_collection"
        mock_collection.status = "green"
        mock_collection.vectors_count = 100
        mock_collection.points_count = 100
        mock_client.get_collection.return_value = mock_collection
        
        # Create the indexer
        indexer = VectorIndexer()
        
        # Call the method
        result = await indexer.get_collection_info()
        
        # Assertions
        assert result == {
            "name": "test_collection",
            "status": "green",
            "vectors_count": 100,
            "points_count": 100,
        }
        mock_client.get_collection.assert_called_once_with(collection_name=indexer.collection_name)
