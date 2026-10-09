from abc import ABC, abstractmethod

class LLMProvider(ABC):
    
    @abstractmethod
    async def generate_response(self, user_message: str) -> str:
        pass