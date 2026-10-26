from unittest.mock import AsyncMock

import pytest

from app.agents.decision_service import ToolDecision
from app.agents.graph import agent_graph
from app.agents import graph as graph_module
from app.agents.response_service import GroundedAnswer


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
    mock_decide = AsyncMock(
        return_value=ToolDecision(
            tool="search_runbooks",
            query="",
        )
    )

    mock_call = AsyncMock(
        return_value={
            "result": [
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
        }
    )

    mock_generate = AsyncMock(
        return_value=GroundedAnswer(
            answer=(
                "Inspect Kubernetes pod events, " "container logs, and resource limits."
            ),
            sources=["runbooks/kubernetes-pod-runbook.md"],
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

    question = "Why is my kubernetes crashing?"

    result = await agent_graph.ainvoke({"question": question})

    assert result["status"] == "success"
    assert "Kubernetes" in result["answer"]

    mock_call.assert_awaited_once_with(
        "search_runbooks",
        arguments={
            "query": question,
            "top_k": 3,
        },
    ),

    mock_generate.assert_awaited_once
