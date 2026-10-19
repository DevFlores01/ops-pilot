from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService

class RetrievalService:
    
    def __init__(self):
        self.db = DatabaseService()
        self.embedding = EmbeddingService()
        
    async def search(
        self,
        query: str,
        top_k: int = 3
    ) -> list[dict]:
        
        if not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")
        
        # Convert the users question into embedding
        query_vector = await self.embedding.embed_text(query)
        
        if len(query_vector) != 768:
            raise ValueError("Unexpected embedding dimensions")
        
        vector_literal = (
            "[" + ",".join(map(str, query_vector)) + "]"
        )
        
        # Search for the nearest document vectors.
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        document_key,
                        chunk_index,
                        content,
                        embedding <=> %s::vector AS distance
                    FROM document_chunks
                    ORDER BY embedding <=> %s:: vector
                    LIMIT %s
                    """,
                    (
                        vector_literal,
                        vector_literal,
                        top_k,
                    )
                )
                
                rows = cursor.fetchall()
                
        return [
            {
                "document_key": row[0],
                "chunk_index": row[1],
                "content": row[2],
                "cosine_distance": float(row[3]),
                "similarity": 1.0 - float(row[3]),
            }
            for row in rows
        ]