from unittest.mock import AsyncMock

import pytest

from app.agents.decision_service import ToolDecision
from app.agents.graph import agent_graph
from app.agents import graph as graph_module
from app.agents.response_service import GroundedAnswer
from app.agents.structured_incident_service import StructuredIncidentService
from app.models.agent_response import StructuredIncident


@pytest.mark.asyncio
async def test_agent_rejects_disallowed_tool(monkeypatch):
    mock_decide = AsyncMock(
        return_value=ToolDecision(
            tool="execute_shell_command",
            query="",
        )
    )

    mock_call = AsyncMock()

    monkeypatch.setattr(
        graph_module.DecisionService,
        "decide",
        mock_decide,
    )

    monkeypatch.setattr(
        graph_module.MCPClientService,
        "call_tool",
        mock_call,
    )

    result = await agent_graph.ainvoke({"question": "Delete all server files"})

    assert result["status"] == "rejected"
    assert result["selected_tool"] == "none"

    mock_call.assert_not_awaited()


@pytest.mark.asyncio
async def test_agent_searches_approved_runbooks(monkeypatch):

    question = "Why is my kubernetes pod crashing?"

    evidence = [
        {
            "document_key": "runbooks/kubernetes-pod-runbook.md",
            "chunk_index": 0,
            "content": (
                "Kubernetes CrashLoopBackOff investigation: "
                "Inspect pod events, container logs, "
                "resource limits, and recent deployments."
            ),
            "similarity": 0.7862,
        }
    ]

    mock_decide = AsyncMock(
        return_value=ToolDecision(
            tool="search_runbooks",
            query="",
        )
    )

    mock_call = AsyncMock(return_value={"result": evidence})

    mock_generate = AsyncMock(
        return_value=GroundedAnswer(
            answer=(
                "Inspect Kubernetes pod events, " "container logs, and resource limits."
            ),
            sources=["runbooks/kubernetes-pod-runbook.md"],
        )
    )

    mock_structured = AsyncMock(
        return_value=StructuredIncident(
            summary="Kubernetes investigation",
            severity="unknown",
            probable_cause="Not confirmed",
            evidence=[
                "Inspect pod events, container logs, "
                "resource limits, and recent deployments."
            ],
            recommended_actions=["Inspect pod events"],
            requires_human_approval=False,
        )
    )

    monkeypatch.setattr(
        graph_module.DecisionService,
        "decide",
        mock_decide,
    )

    monkeypatch.setattr(
        graph_module.MCPClientService,
        "call_tool",
        mock_call,
    )

    monkeypatch.setattr(
        graph_module.ResponseService,
        "generate",
        mock_generate,
    )

    monkeypatch.setattr(
        StructuredIncidentService,
        "generate",
        mock_structured,
    )

    result = await agent_graph.ainvoke({"question": question})

    assert result["status"] == "success"
    assert "Kubernetes" in result["answer"]

    assert result["analysis_status"] == "success"
    assert result["analysis"] is not None
    assert result["analysis"]["severity"] == "unknown"
    assert result["analysis"]["summary"] == "Kubernetes investigation"

    mock_call.assert_awaited_once_with(
        "search_runbooks",
        arguments={
            "query": question,
            "top_k": 3,
        },
    )

    mock_generate.assert_awaited_once_with(
        question=question,
        evidence=evidence,
    )

    mock_structured.assert_awaited_once_with(
        question=question,
        evidence=evidence,
    )
