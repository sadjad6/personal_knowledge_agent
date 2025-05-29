from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from ...services.qa import get_qa_response
from ...services.summarizer import generate_daily_summary
from ...config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ask")
async def ask_question(
    q: str = Query(..., description="The question to ask about your knowledge base"),
    limit: int = Query(5, description="Maximum number of results to return"),
):
    """
    Ask a question about your personal knowledge base.
    
    This endpoint uses RAG to find relevant information from your notes and generate
    an answer using the configured LLM.
    """
    try:
        logger.info(f"Processing question: {q}")
        response = await get_qa_response(q, limit=limit)
        return {"question": q, "answer": response}
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def trigger_summary():
    """
    Manually trigger the generation of a summary of recent notes.
    
    This will generate a summary of notes that have been added or modified recently
    and save it to the summaries directory.
    """
    try:
        logger.info("Manually triggering summary generation")
        summary = await generate_daily_summary()
        return {"status": "success", "summary": summary}
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_status():
    """
    Get the current status of the knowledge base.
    
    Returns information about the number of documents indexed and other
    relevant statistics.
    """
    # TODO: Implement actual status checking
    return {
        "status": "operational",
        "vector_store": "Qdrant",
        "llm": settings.MODEL_NAME,
        "notes_dir": str(settings.NOTES_DIR),
        "summaries_dir": str(settings.SUMMARIES_DIR),
    }

@router.post("/ingest")
async def ingest_notes():
    """
    Manually trigger ingestion of notes from the notes directory.
    
    This will process all notes in the configured notes directory and add them
    to the vector store.
    """
    try:
        # TODO: Implement actual ingestion logic
        return {"status": "ingestion started"}
    except Exception as e:
        logger.error(f"Error during ingestion: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
