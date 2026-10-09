from openai import AsyncOpenAI

from app.core.config import settings
from app.services.llm.base import LLMProvider

class OpenAIProvider(LLMProvider):
    
    def __init__(self):
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is requried when using OpenAI"
            )
            
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )
        
    async def generate_response(self, user_message: str) -> str:
        
        response = await self.client.response.create(
            model=settings.openai_model,
            instructions=(
                "You are OpsPilot, an AI assistant for "
                "production operations engineers. "
                "Do not claim to have checked infrastructure "
                "unless tools supplied that information."
            ),
            input=user_message,
        )
        
        return response.output_text