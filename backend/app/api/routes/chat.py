import logging
from fastapi import APIRouter, HTTPException

from app.models.chat import ChatRequest, ChatResponse
from app.services.llm.factory import get_llm_provider

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"]
)

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    
    try:
        llm = get_llm_provider()
        
        response = await llm.generate_response(
            request.message
        )
        
        return ChatResponse(
            message=response,
            status="success"
        )
        
    except Exception as exc:
        logger.exception("LLM error")
            
        raise HTTPException(
            status_code=500,
            detail="Failed to generate AI response"
        ) from exc