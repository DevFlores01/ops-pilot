from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app
from app.services.mcp_client_service import MCPClientService

client = TestClient(app)

HEADERS = {"X_API_KEY": settings.opspilot_api_key}


def test_mcp_listing_failure_returns_502(monkeypatch):
    mock_call = AsyncMock(side_effect=RuntimeError("MCP unavailable"))

    monkeypatch.setattr(
        MCPClientService,
        "call_tool",
        mock_call,
    )

    response = client.get(
        "/api/v1/tools/runbooks",
        headers=HEADERS,
    )

    assert response.status_code == 502
    assert response.json()["detail"] == ("Unable to list runbooks")


def test_mcp_search_failure_returns_502(monkeypatch):
    mock_call = AsyncMock(side_effect=RuntimeError("MCP unavailable"))

    monkeypatch.setattr(
        MCPClientService,
        "call_tool",
        mock_call,
    )

    response = client.post(
        "/api/v1/tools/search",
        json={
            "query": "Kubernetes pod failure",
            "top_k": 3,
        },
        headers=HEADERS,
    )

    assert response.status_code == 502
    assert response.json()["detail"] == ("Unable to search runbooks")
