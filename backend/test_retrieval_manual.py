import asyncio

from app.services.retrieval_service import RetrievalService

async def main():
    service = RetrievalService()
    
    question = (
        "Why is the payment API returning HTTP 500 errors?"
    )
    
    results = await service.search(
        query=question,
        top_k=3
    )
    
    print("Question:", question)
    print("Results found:", len(results))
    
    for index, result in enumerate(results, start=1):
        print(f"\n--- Result {index} ---")
        print("Document:", result["document_key"])
        print("Chunk:", result["chunk_index"])
        print("Similarity:", round(result["similarity"], 4))
        print("Content:")
        print(result["content"])
        
    assert len(results) > 0
    assert results[0]["document_key"] == (
        "runbooks/payment-api-runbook.md"
    )
    
    print("\nPASS: Semantic retrieval successful")
    
if __name__ == "__main__":
    asyncio.run(main())