from openai import AsyncOpenAI

from app.core.config import settings

class LLMService:
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key
        )
        
    async def generate_response(self, user_message: str) -> str:
        
        response = await self.client.responses.create(
            model=settings.openai_model,
            instructions=(
                "You are OpsPilot, an AI assitant for production "
                "operations engineers. Help investigate infrastructure, "
                "application, networking, database, and operational issues. "
                "Do not claim to have checked logs, metrics, databases, "
                "servers, or infrastructire unless actual tools provided "
                "that information."
            ),
            input=user_message,
        )
        
        return response.output_text
    
llm_service = LLMService()