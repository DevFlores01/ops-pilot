from app.core.config import settings
from app.services.llm.base import LLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider

def get_llm_provider() -> LLMProvider:
    
    provider = settings.llm_provider.lower()
    
    if provider == "ollama":
        return OllamaProvider()
    
    if provider == "openai":
        return OpenAIProvider()
    
    raise ValueError(
        f"Unsupported LLM provider: {settings.llm_provider}"
    )