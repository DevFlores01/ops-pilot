import logging

import httpx
from fastapi import APIRouter, HTTPException

from app.models.rag import RAGRequest, RAGResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/rag",
    tags=["RAG"],
)

@router.post("/ask", response_model=RAGResponse)
async def ask_rag(request: RAGRequest):
    
    try:
        service = RAGService()
        
        return await service.ask(
            question=request.question,
            top_k=request.top_k,
        )
        
    except httpx.HTTPError:
        logger.exception("Ollama request failed")
        raise HTTPException(
            status_code=502,
            detail="AI model service is unavailable",
        )
        
    except Exception:
        logger.exception("RAG request failed")
        raise HTTPException(
            status_code=500,
            detail="RAG processing failed",
        )