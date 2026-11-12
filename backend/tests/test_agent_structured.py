from unittest.mock import AsyncMock

import pytest

from app.agents.graph import structured_analysis_node
from app.agents.structured_incident_service import StructuredIncidentService
from app.models.agent_response import StructuredIncident

EVIDENCE = {
    "document_key": "runbooks/kubernetes-pod-runbook.md",
    "chunk_index": 0,
    "similarity": 0.7862,
    "content": "Inspect Kubernetes pod events and logs",
}


@pytest.mark.asyncio
async def test_structured_analysis_success(monkeypatch):
    incident = StructuredIncident(
        summary="Kubernetes pod is restarting.",
        severity="unknown",
        probable_cause="Not confirmed.",
        evidence=[EVIDENCE["content"].strip()],
        recommended_actions=["Inspect pod events."],
        requires_human_approval=False,
    )

    mock_generate = AsyncMock(return_value=incident)

    monkeypatch.setattr(
        StructuredIncidentService,
        "generate",
        mock_generate,
    )

    question = "Why is Kubernetes crashing?"

    result = await structured_analysis_node(
        {
            "question": question,
            "selected_tool": "search_runbooks",
            "tool_result": {"result": [EVIDENCE]},
            "status": "success",
        }
    )

    assert result["analysis_status"] == "success"
    assert result["analysis"] is not None
    assert result["analysis"]["severity"] == "unknown"
    assert result["analysis"]["summary"] == ("Kubernetes pod is restarting.")

    assert len(result["sources"]) == 1
    assert isinstance(result["sources"][0], dict)

    assert result["sources"][0]["document_key"] == (
        "runbooks/kubernetes-pod-runbook.md"
    )

    assert result["sources"][0]["chunk_index"] == 0
    assert result["sources"][0]["similarity"] == 0.7862

    mock_generate.assert_awaited_once_with(
        question=question,
        evidence=[EVIDENCE],
    )


@pytest.mark.asyncio
async def test_invalid_evidence_blocks_generation(monkeypatch):
    mock_generate = AsyncMock()

    monkeypatch.setattr(
        StructuredIncidentService,
        "generate",
        mock_generate,
    )

    result = await structured_analysis_node(
        {
            "question": "Why is Kubernetes crashing?",
            "selected_tool": "search_runbooks",
            "tool_result": {
                "result": [
                    {
                        **EVIDENCE,
                        "content": "",
                    }
                ]
            },
            "status": "success",
        }
    )

    assert result["analysis"] is None
    assert result["analysis_status"] == "insufficient_evidence"
    mock_generate.assert_not_awaited()


@pytest.mark.asyncio
async def test_structured_generation_failure(monkeypatch):
    mock_generate = AsyncMock(side_effect=RuntimeError("Ollama unavailable"))

    monkeypatch.setattr(
        StructuredIncidentService,
        "generate",
        mock_generate,
    )

    result = await structured_analysis_node(
        {
            "question": "Why is Kubernetes crashing?",
            "selected_tool": "search_runbooks",
            "tool_result": {"result": [EVIDENCE]},
            "status": "success",
        }
    )

    assert result["analysis"] is None
    assert result["analysis_status"] == "generation_error"
