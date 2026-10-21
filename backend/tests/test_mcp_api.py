from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.services.mcp_client_service import MCPClientService

client = TestClient(app)


def test_search_rejects_invalid_top_k():
    response = client.post(
        "/api/v1/tools/search",
        json={"query": "kubernetes errors", "top_k": 100},
    )

    assert response.status_code == 422


def test_Search_calls_allowlisted_mcp_tool(monkeypatch):
    mock_call = AsyncMock(
        return_value={
            "result": [
                {
                    "document_key": "runbooks/kubernetes-pod-runbook.md",
                    "similarity": 0.7862,
                }
            ]
        }
    )

    monkeypatch.setattr(
        MCPClientService,
        "call_tool",
        mock_call,
    )

    response = client.post(
        "/api/v1/tools/search",
        json={
            "query": "Kubernetes CrashLoopBackOff",
            "top_k": 3,
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"

    mock_call.assert_awaited_once_with(
        "search_runbooks",
        arguments={
            "query": "Kubernetes CrashLoopBackOff",
            "top_k": 3,
        },
    )
