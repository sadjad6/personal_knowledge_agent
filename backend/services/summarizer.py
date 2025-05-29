import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from ...config import settings
from ..rag.indexer import VectorIndexer

logger = logging.getLogger(__name__)

# Initialize the vector indexer
indexer = VectorIndexer()

# Initialize the LLM
llm = ChatOllama(
    base_url=settings.OLLAMA_BASE_URL,
    model=settings.MODEL_NAME,
    temperature=0.2,  # Slightly higher temperature for more creative summaries
)

# Define the summarization prompt
SUMMARY_PROMPT = """You are an expert at summarizing and synthesizing information. 
Your task is to create a concise, well-organized daily summary of the following notes.

Focus on:
1. Key themes and topics
2. Important decisions or action items
3. New information or insights
4. Any follow-up needed

Be concise but comprehensive. Use bullet points and organize by topic when possible.

Notes to summarize:
{context}

Concise Daily Summary:"""

async def generate_daily_summary() -> str:
    """
    Generate a summary of recent notes and save it to the summaries directory.
    
    Returns:
        The generated summary text
    """
    try:
        logger.info("Starting daily summary generation")
        
        # 1. Get recently added or modified notes (last 24 hours)
        recent_notes = await _get_recent_notes(days=1)
        
        if not recent_notes:
            summary_text = "No new or updated notes in the last 24 hours."
        else:
            # 2. Format the notes for summarization
            formatted_notes = _format_notes_for_summarization(recent_notes)
            
            # 3. Generate the summary using the LLM
            summary_text = await _generate_summary_with_llm(formatted_notes)
        
        # 4. Save the summary to a file
        await _save_summary(summary_text)
        
        return summary_text
        
    except Exception as e:
        error_msg = f"Error generating daily summary: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return error_msg

async def _get_recent_notes(days: int = 1) -> List[Dict[str, Any]]:
    """
    Retrieve notes that were added or modified in the last N days.
    
    Args:
        days: Number of days to look back
        
    Returns:
        List of recent notes with content and metadata
    """
    try:
        # Calculate the cutoff date
        cutoff_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
        
        # Search for recent documents
        recent_docs = await indexer.similarity_search(
            query="recent updates",  # Generic query to get recent documents
            k=50,  # Limit the number of results
            filter={"ingestion_time": {"$gt": cutoff_date}}
        )
        
        # Process and deduplicate results by source
        seen_sources = set()
        unique_notes = []
        
        for doc in recent_docs:
            source = doc['metadata'].get('source')
            if source and source not in seen_sources:
                seen_sources.add(source)
                unique_notes.append({
                    'source': source,
                    'title': doc['metadata'].get('title', 'Untitled'),
                    'content': doc['content'],
                    'last_modified': doc['metadata'].get('last_modified', 'Unknown'),
                })
        
        return unique_notes
        
    except Exception as e:
        logger.error(f"Error fetching recent notes: {str(e)}", exc_info=True)
        return []

def _format_notes_for_summarization(notes: List[Dict[str, Any]]) -> str:
    """
    Format notes into a string suitable for summarization.
    
    Args:
        notes: List of note dictionaries with content and metadata
        
    Returns:
        Formatted string of notes
    """
    formatted_notes = []
    
    for i, note in enumerate(notes, 1):
        formatted_note = f"""
        --- Note {i}: {note.get('title', 'Untitled')} ---
        Source: {note.get('source', 'Unknown')}
        Last Modified: {note.get('last_modified', 'Unknown')}
        
        {note.get('content', '')}
        """
        formatted_notes.append(formatted_note)
    
    return "\n\n".join(formatted_notes)

async def _generate_summary_with_llm(formatted_notes: str) -> str:
    """
    Generate a summary using the LLM.
    
    Args:
        formatted_notes: Formatted string of notes to summarize
        
    Returns:
        Generated summary text
    """
    try:
        # Set up the summarization chain
        prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)
        
        chain = (
            {"context": lambda x: x}
            | prompt
            | llm
            | StrOutputParser()
        )
        
        # Generate the summary
        summary = await chain.ainvoke(formatted_notes)
        return summary.strip()
        
    except Exception as e:
        logger.error(f"Error generating summary with LLM: {str(e)}", exc_info=True)
        return f"Error generating summary: {str(e)}"

async def _save_summary(summary_text: str) -> None:
    """
    Save the summary to a file in the summaries directory.
    
    Args:
        summary_text: The summary text to save
    """
    try:
        # Create the summaries directory if it doesn't exist
        settings.SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Generate a filename with the current date and time
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"summary_{timestamp}.md"
        filepath = settings.SUMMARIES_DIR / filename
        
        # Write the summary to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"# Daily Summary - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(summary_text)
        
        logger.info(f"Summary saved to {filepath}")
        
    except Exception as e:
        logger.error(f"Error saving summary: {str(e)}", exc_info=True)
