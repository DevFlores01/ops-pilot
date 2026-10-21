from fastapi.testclient import TestClient

from app.main import app
from app.core.config import settings

client = TestClient(app)


def test_missing_api_key_rejected():
    response = client.get("/api/v1/tools/runbooks")
    assert response.status_code == 401


def test_invalid_api_key_rejected():
    response = client.get(
        "/api/v1/tools/runbooks",
        headers={"X-API-Key": "Invalid-key"},
    )
    assert response.status_code == 401


def test_valid_api_key_accepted(monkeypatch):
    from unittest.mock import AsyncMock
    from app.services.mcp_client_service import MCPClientService

    mock_call = AsyncMock(return_value={"result": []})

    monkeypatch.setattr(
        MCPClientService,
        "call_tool",
        mock_call,
    )

    response = client.get(
        "/api/v1/tools/runbooks",
        headers={"X_API_Key": settings.opspilot_api_key},
    )

    assert response.status_code == 200
    mock_call.assert_awaited_once()
