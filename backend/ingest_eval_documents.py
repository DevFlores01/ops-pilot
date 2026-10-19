import asyncio

from app.services.ingestion_service import IngestionService

async def main():
    service = IngestionService()
    
    for key in [
        "runbooks/redis-cache-runbook.md",
        "runbooks/kubernetes-pod-runbook.md",
    ]:
        result = await service.ingest(key)
        print(result)
        
if __name__ == "__main__":
    asyncio.run(main())