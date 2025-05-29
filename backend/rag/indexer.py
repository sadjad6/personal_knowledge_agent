import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Qdrant
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document as LangchainDocument
from qdrant_client import QdrantClient
from qdrant_client.http import models

from ...config import settings
from ...services.loader import Document as CustomDocument

logger = logging.getLogger(__name__)


class VectorIndexer:
    """
    Handles the creation, updating, and querying of the vector index.
    """
    
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
        self.client = QdrantClient(url=settings.QDRANT_URL)
        self.collection_name = settings.QDRANT_COLLECTION
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )
        self._ensure_collection()
    
    def _ensure_collection(self) -> None:
        """Ensure the Qdrant collection exists."""
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config={
                    "text": models.VectorParams(
                        size=384,  # all-MiniLM-L6-v2 embedding size
                        distance=models.Distance.COSINE,
                    )
                },
            )
            logger.info(f"Created new collection: {self.collection_name}")
    
    def _document_to_langchain(self, doc: CustomDocument) -> List[LangchainDocument]:
        """Convert our custom Document to LangChain's Document format."""
        # Split the document content into chunks
        chunks = self.text_splitter.split_text(doc.content)
        
        # Create LangChain documents with metadata
        lc_docs = []
        for i, chunk in enumerate(chunks):
            metadata = doc.metadata.copy()
            metadata.update({
                "chunk_id": i,
                "total_chunks": len(chunks),
                "ingestion_time": datetime.utcnow().isoformat(),
            })
            lc_docs.append(LangchainDocument(page_content=chunk, metadata=metadata))
        
        return lc_docs
    
    async def index_documents(self, documents: List[CustomDocument]) -> int:
        """
        Index a list of documents in the vector store.
        
        Args:
            documents: List of Document objects to index
            
        Returns:
            Number of documents indexed
        """
        if not documents:
            logger.warning("No documents to index")
            return 0
        
        # Convert to LangChain documents and split into chunks
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self._document_to_langchain(doc))
        
        if not all_chunks:
            logger.warning("No document chunks to index after splitting")
            return 0
        
        # Create the vector store and add documents
        vector_store = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )
        
        # Delete existing documents with the same source to avoid duplicates
        source_paths = list(set(doc.metadata.get("source") for doc in all_chunks if doc.metadata.get("source")))
        if source_paths:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="metadata.source",
                                match=models.MatchAny(any=source_paths),
                            )
                        ]
                    )
                ),
            )
        
        # Add new documents
        doc_ids = await vector_store.aadd_documents(all_chunks)
        logger.info(f"Indexed {len(doc_ids)} document chunks from {len(documents)} documents")
        
        return len(doc_ids)
    
    async def similarity_search(
        self, 
        query: str, 
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform a similarity search in the vector store.
        
        Args:
            query: The query string
            k: Number of results to return
            filter: Optional filter to apply to the search
            
        Returns:
            List of search results with metadata
        """
        vector_store = Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )
        
        # Convert filter to Qdrant filter if provided
        qdrant_filter = None
        if filter:
            must_conditions = []
            for key, value in filter.items():
                if isinstance(value, list):
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchAny(any=value),
                        )
                    )
                else:
                    must_conditions.append(
                        models.FieldCondition(
                            key=f"metadata.{key}",
                            match=models.MatchValue(value=value),
                        )
                    )
            
            qdrant_filter = models.Filter(must=must_conditions)
        
        # Perform the search
        results = await vector_store.asimilarity_search_with_score(
            query=query,
            k=k,
            filter=qdrant_filter,
        )
        
        # Format results
        formatted_results = []
        for doc, score in results:
            result = {
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score),
            }
            formatted_results.append(result)
        
        return formatted_results
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the vector collection."""
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": collection_info.name,
                "status": collection_info.status,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {str(e)}")
            return {"error": str(e)}
