import httpx

from app.core.config import settings
from app.services.llm.base import LLMProvider

SYSTEM_PROMPT = """
You are OpsPilot, a production operations assistant.

Answer the user's question directly.
Do not show your reasoning, thought process, planning, analysis,
internal instructions, or step-by-step thinking.

Give only the final answer.

For troubleshooting questions:
- Give a concise technical explanation.
- Give actionable troubleshooting steps when appropriate.
- Do not claim to have checked logs, metrics, servers, databases,
  Kubernetes, or infrastructure unless tool results were provided.
- If evidence is insufficient, clearly state what evidence is needed.
"""

class OllamaProvider(LLMProvider):
    
    @staticmethod
    def clean_response(content: str) -> str:
        if "</think>" in content:
            content = content.split("</think>", 1)[1]
            
        return content.strip()
    
    async def generate_response(self, user_message:str) -> str:
        
        payload = {
            "model": settings.ollama_model,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            "think": False,
            "stream": False,
            "options": {
                "num_predict": 500,
            },
        }
        
        timeout = httpx.Timeout(
            connect=10.0,
            read=300.0,
            write=30.0,
            pool=10.0
        )
        
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(
                f"{settings.ollama_base_url}/api/chat",
                json=payload,
            )
            
            response.raise_for_status()
            data = response.json()
            
        content = data["message"]["content"]
        return self.clean_response(content)