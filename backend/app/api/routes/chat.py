from fastapi import APIRouter

from app.models.chat import ChatRequest, ChatResponse

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["chat"]
)

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    
    return ChatResponse(
        message=f"OpsPilot received: {request.message}",
        status="received"
    )