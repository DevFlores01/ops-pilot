import asyncio

from app.services.retrieval_service import RetrievalService

CASES = [
     (
        "Why is PostgreSQL connection exhaustion "
        "affecting the payment API?",
        "runbooks/payment-api-runbook.md",
    ),
    (
        "Why is Redis experiencing high cache misses?",
        "runbooks/redis-cache-runbook.md",
    ),
    (
        "Why is my Kubernetes pod in CrashLoopBackOff?",
        "runbooks/kubernetes-pod-runbook.md",
    ),
]

async def main():
    service = RetrievalService()
    passed = 0
    
    for question, expected_key in CASES:
        results = await service.search(
            query=question,
            top_k=3,
        )
        
        actual_key = (
            results[0]["document_key"]
            if results else None
        )
        
        success = actual_key == expected_key
        passed += int(success)
        
        print("\nQuestion:", question)
        print("Expected:", expected_key)
        print("Retrieved:", actual_key)
        print("Result:", "PASS" if success else "FAIL")
        
    accuracy = passed / len(CASES)
    
    print(f"\nRecall@1: {accuracy:.2%}")
    
    assert passed == len(CASES), (
        "One or more retrieval cases failed"
    )

if __name__ == "__main__":
    asyncio.run(main())