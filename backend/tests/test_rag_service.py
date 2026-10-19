from unittest.mock import AsyncMock

import pytest

from app.services.rag_service import RAGService

@pytest.mark.asyncio
async def test_unrelated_question_returns_insufficient_context(
    monkeypatch,
):
    service = RAGService()
    
    service.retrieval.search = AsyncMock(
        return_value=[
            {
            "document_key": "runbooks/payment-api-runbook.md",
            "chunk_index": 0,
            "content": "Investigate PostgreSQL connections.",
            "cosine_distance": 0.62,
            "similarity": 0.38,
            }
        ]
    )
    
    monkeypatch.setattr(
        "app.services.rag_service.settings.rag_min_similarity",
        0.55,
    )
    
    result = await service.ask(
        "What is the company's annual revenue?"
    )
    
    assert result["status"] == "insufficient_context"
    assert result["sources"] == []
    assert "do not" in result["answer"].lower()
    
@pytest.mark.asyncio
async def test_no_documents_returns_insufficient_context():
    service = RAGService()
    
    service.retrieval.search = AsyncMock(return_value=[])
    
    result = await service.ask(
        "What caused the payment API incident?"
    )
    
    assert result["status"] == "insufficient_context"
    assert result["sources"] == []