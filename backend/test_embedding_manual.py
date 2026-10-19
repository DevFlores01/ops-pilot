import asyncio

from app.services.embedding_service import EmbeddingService

async def main():
    service = EmbeddingService()
    
    text = "PostgreSQL connection pool exhausted"
    
    embedding = await service.embed_text(text)
    
    print("Input:", text)
    print("Embedding dimension:", len(embedding))
    print("First 10 values:", embedding[:10])
    
    assert len(embedding) == 768
    assert all(isinstance(value, float) for value in embedding)
    
    print("PASS: Embedding generated successfully")
    
if __name__ == "__main__":
    asyncio.run(main())