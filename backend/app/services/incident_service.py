from app.core.config import settings
from app.models.incident import IncidentAnalysis
from app.services.llm.ollama_provider import OllamaProvider

class IncidentService:
    
    def __init__(self):
        if settings.llm_provider.lower() != "ollama":
            raise ValueError(
                "Incident analysis currently supports Ollama"
            )
            
        self.llm = OllamaProvider()
        
    async def analyze (
        self,
        description: str
    ) -> IncidentAnalysis:
        
        return await self.llm.analyze_incident(description)