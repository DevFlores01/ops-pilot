import hashlib

from app.rag.chunker import chunk_text
from app.services.s3_service import S3Service
from app.services.database_service import DatabaseService
from app.services.embedding_service import EmbeddingService

class IngestionService:
    
    def __init__(self):
        self.s3 = S3Service()
        self.db = DatabaseService()
        self.embedding = EmbeddingService()
        
    async def ingest(self, document_key: str) -> dict:
        
        # 1. Download documen to local S3.
        response = self.s3.client.get_object(
            Bucket=self.s3.bucket,
            Key=document_key
        )
        
        document_bytes = response["Body"].read()
        document_text = document_bytes.decode("utf-8")
        
        # 2. Calculate a document fingerprint
        document_hash = hashlib.sha256(
            document_bytes
        ).hexdigest()
        
        # 3. Split into chunks
        chunks = chunk_text(document_text)
        
        if not chunks:
            raise ValueError("Document contains no usable text")
        
        # 4. Generate embeddings before opening a database transaction.
        records = []
        
        for index, chunk in enumerate(chunks):
            vector = await self.embedding.embed_text(chunk)
                
            if len(vector) != 768:
                raise ValueError(
                    f"Expected 768 dimensions, got {len(vector)}"
                )
                    
            records.append((index, chunk, vector))
                
        # 5. Replace this documents chunks atomically. If insertion fails, the transaction rolls back.
        with self.db.connect() as conn:
            with conn.cursor() as cursor:
                
                # Serialize ingestion for this document key.
                cursor.execute(
                    "SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))",
                    (document_key,)
                )
                
                cursor.execute(
                    "DELETE FROM document_chunks WHERE document_key = %s",
                    (document_key,)
                )
                
                for index, chunk, vector in records:
                    vector_literal = (
                        "[" + ",".join(map(str, vector)) + "]"
                    )
                    
                    cursor.execute(
                        """
                        INSERT INTO document_chunks
                            (document_key, chunk_index, content, embedding)
                        VALUES (%s, %s, %s, %s::vector)
                        """,
                        (
                            document_key,
                            index,
                            chunk,
                            vector_literal,
                        )
                    )
                    
        return {
            "document_key": document_key,
            "document_hash": document_hash,
            "chunks_created": len(records),
            "status": "success",
        }