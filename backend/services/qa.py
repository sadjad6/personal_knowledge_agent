import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from ...config import settings
from ..rag.indexer import VectorIndexer

logger = logging.getLogger(__name__)

# Initialize the vector indexer
indexer = VectorIndexer()

# Define the prompt template for question answering
QA_PROMPT = """You are a helpful AI assistant that answers questions based on the provided context. 
Use the following pieces of context to answer the question at the end. 
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}
Helpful Answer:"""

# Initialize the LLM
llm = ChatOllama(
    base_url=settings.OLLAMA_BASE_URL,
    model=settings.MODEL_NAME,
    temperature=0.1,
)

async def get_qa_response(question: str, limit: int = 5) -> str:
    """
    Get an answer to a question using the RAG pipeline.
    
    Args:
        question: The question to answer
        limit: Maximum number of context chunks to use
        
    Returns:
        The generated answer
    """
    try:
        logger.info(f"Processing question: {question}")
        
        # 1. Retrieve relevant documents
        search_results = await indexer.similarity_search(
            query=question,
            k=limit,
        )
        
        if not search_results:
            return "I couldn't find any relevant information to answer your question."
        
        # 2. Format the context
        context = "\n\n---\n\n".join([
            f"Source: {result['metadata'].get('source', 'Unknown')}\n"
            f"Content: {result['content']}"
            for result in search_results
        ])
        
        # 3. Set up the RAG chain
        prompt = ChatPromptTemplate.from_template(QA_PROMPT)
        
        chain = (
            {"context": lambda x: context, "question": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # 4. Generate the response
        response = await chain.ainvoke(question)
        
        # 5. Add sources to the response
        sources = list(set(
            result['metadata'].get('source', 'Unknown')
            for result in search_results
        ))
        
        return f"{response}\n\nSources: {', '.join(sources) if sources else 'No sources found'}"
        
    except Exception as e:
        logger.error(f"Error generating QA response: {str(e)}", exc_info=True)
        return f"I encountered an error while processing your question: {str(e)}"

async def get_recent_updates(days: int = 7) -> List[Dict[str, Any]]:
    """
    Get recently added or updated documents.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of recent documents with metadata
    """
    try:
        # Calculate the cutoff date
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Search for recent documents
        recent_docs = await indexer.similarity_search(
            query="recent updates",  # Generic query to get recent documents
            k=20,  # Limit the number of results
            filter={"ingestion_time": {"$gt": cutoff_date}}
        )
        
        # Process and deduplicate results by source
        seen_sources = set()
        unique_docs = []
        
        for doc in recent_docs:
            source = doc['metadata'].get('source')
            if source and source not in seen_sources:
                seen_sources.add(source)
                unique_docs.append({
                    'source': source,
                    'title': doc['metadata'].get('title', 'Untitled'),
                    'last_modified': doc['metadata'].get('last_modified', 'Unknown'),
                    'snippet': doc['content'][:200] + '...',  # First 200 chars as preview
                })
        
        return unique_docs
        
    except Exception as e:
        logger.error(f"Error fetching recent updates: {str(e)}", exc_info=True)
        return []

async def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the vector collection.
    
    Returns:
        Dictionary with collection statistics
    """
    try:
        return await indexer.get_collection_info()
    except Exception as e:
        logger.error(f"Error getting collection stats: {str(e)}", exc_info=True)
        return {"error": str(e)}
