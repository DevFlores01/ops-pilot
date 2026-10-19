import asyncio

from app.services.ingestion_service import IngestionService

async def main():
    
    service = IngestionService()
    
    result = await service.ingest(
        "runbooks/payment-api-runbook.md"
    )
    
    print("Document:", result["document_key"])
    print("SHA256:", result["document_hash"])
    print("Chunks created:", result["chunks_created"])
    print("Status:", result["status"])
    
    assert result["status"] == "success"
    assert result["chunks_created"] > 0
    
    print("PASS: S3 document ingested into PostgreSQL")
    
if __name__ == "__main__":
    asyncio.run(main())