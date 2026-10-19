import httpx

from app.core.config import settings

class EmbeddingService:
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.model = settings.embedding_model
        
    async def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Cannot embed empty text")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/api/embed",
                json={
                    "model": self.model,
                    "input": text
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
        embeddings = data["embeddings"]
        
        if len(embeddings) != 1:
            raise ValueError(
                "Expected exactly one embedding"
            )
            
        return embeddings[0]