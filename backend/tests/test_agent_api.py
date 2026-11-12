from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.routes import agent as agent_route
from app.core.config import settings
from app.main import app

client = TestClient(app)

URL = "/api/v1/agent/investigate"

HEADERS = {"X_API_KEY": settings.opspilot_api_key}


def test_agent_requires_authentication():
    response = client.post(
        URL,
        json={"question": "Why is kubernetes crashing?"},
    )

    assert response.status_code == 401


def test_agent_rejects_empty_question():
    response = client.post(
        URL,
        headers=HEADERS,
        json={"question": "     "},
    )

    assert response.status_code == 422


def test_agent_returns_structured_analysis(monkeypatch):
    question = "Why is Kubernetes crashing?"

    mock_invoke = AsyncMock(
        return_value={
            "question": question,
            "status": "success",
            "answer": "Inspect pod events and logs.",
            "analysis_status": "success",
            "analysis": {
                "summary": "Kubernetes pod is restarting.",
                "severity": "unknown",
                "probable_cause": "Not confirmed",
                "evidence": ["1. Inspect pod events."],
                "recommended_actions": [],
                "requires_human_approval": False,
            },
            "sources": [
                {
                    "document_key": "runbooks/kubernetes-pod-runbook.md",
                    "chunk_index": 0,
                    "similarity": 0.7862,
                }
            ],
            "tool_result": {"internal_data": "should_not_be_exposed"},
        }
    )

    monkeypatch.setattr(
        agent_route,
        "agent_graph",
        SimpleNamespace(ainvoke=mock_invoke),
    )

    response = client.post(
        URL,
        headers=HEADERS,
        json={"question": question},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "success"
    assert data["analysis_status"] == "success"
    assert data["analysis"]["severity"] == "unknown"
    assert isinstance(data["sources"][0], dict)

    # Internal LangGraph state must not leak.
    assert "tool_result" not in data

    mock_invoke.assert_awaited_once_with(
        {"question": question},
        config={"recursion_limit": 10},
    )


def test_agent_failure_returns_safe_error(monkeypatch):
    mock_invoke = AsyncMock(side_effect=RuntimeError("Internal model failure"))

    monkeypatch.setattr(
        agent_route,
        "agent_graph",
        SimpleNamespace(ainvoke=mock_invoke),
    )

    response = client.post(
        URL,
        headers=HEADERS,
        json={"question": "Investigate payment API errors"},
    )

    assert response.status_code == 502
    assert "Internal model failure" not in response.text


def test_unrelated_question_can_be_rejected(monkeypatch):
    mock_invoke = AsyncMock(
        return_value={
            "status": "rejected",
            "answer": (
                "I cannot use the available operational tools to answer this request."
            ),
        }
    )

    monkeypatch.setattr(
        agent_route,
        "agent_graph",
        SimpleNamespace(ainvoke=mock_invoke),
    )

    response = client.post(
        URL,
        headers=HEADERS,
        json={"question": "What is the company's annual revenue?"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "rejected"
    assert data["analysis"] is None
    assert data["sources"] == []
