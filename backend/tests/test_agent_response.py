import pytest
from unittest.mock import AsyncMock

from app.agents.graph import generate_answer_node
from app.agents.response_service import GroundedAnswer, ResponseService


@pytest.mark.asyncio
async def test_empty_evidence_blocks_generation(monkeypatch):
    mock_generate = AsyncMock()
    monkeypatch.setattr(
        ResponseService,
        "generate",
        mock_generate,
    )

    result = await generate_answer_node(
        {
            "question": "Why is the payment API failing?",
            "selected_tool": "search_runbooks",
            "tool_result": {"result": []},
            "status": "tool_success",
        }
    )

    assert result["status"] == "insufficient_context"
    mock_generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_relevant_evidence_generates_answer(monkeypatch):
    mock_generate = AsyncMock(
        return_value=GroundedAnswer(
            answer="Inspect Kubernetes pod events and logs.",
            sources=["runbooks/kubernetes-pod-runbook.md"],
        )
    )

    monkeypatch.setattr(ResponseService, "generate", mock_generate)

    result = await generate_answer_node(
        {
            "question": "Why is kubernetes crashing?",
            "selected_tool": "search_runbooks",
            "tool_result": {
                "result": [
                    {
                        "document_key": "runbooks/kubernetes-pod-runbook.md",
                        "content": "Inspect pod events and logs.",
                        "similarity": 0.7862,
                    }
                ]
            },
            "status": "tool_success",
        }
    )

    assert result["status"] == "success"
    assert "Kubernetes" in result["answer"]
    mock_generate.assert_awaited_once()


@pytest.mark.asyncio
async def test_tool_failure_does_not_call_llm(monkeypatch):
    mock_generate = AsyncMock()
    monkeypatch.setattr(
        ResponseService,
        "generate",
        mock_generate,
    )

    result = await generate_answer_node(
        {
            "question": "Why is Redis failing?",
            "selected_tool": "search_runbooks",
            "tool_result": None,
            "status": "tool_error",
        }
    )

    assert result["status"] == "tool_error"
    mock_generate.assert_not_awaited()
