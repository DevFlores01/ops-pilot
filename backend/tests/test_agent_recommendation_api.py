from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.api.routes import agent as agent_route
from app.agents.recommendation_policy import build_recommendations
from app.core.config import settings
from app.main import app

client = TestClient(app)

URL = "/api/v1/agent/investigate"
HEADERS = {"X_API_Key": settings.opspilot_api_key}

EVIDENCE = {
    "document_key": "runbooks/kubernetes-pod-runbook.md",
    "chunk_index": 0,
    "similarity": 0.7862,
    "content": (
        "# Kubernetes Pod Incident Runbook\n"
        "1. Inspect pod events.\n"
        "2. Check container logs.\n"
    ),
}


def test_agent_api_returns_typed_recommendations(monkeypatch):
    question = "Why is my Kubernetes pod restarting?"

    recommendations = build_recommendations([EVIDENCE])

    mock_invoke = AsyncMock(
        return_value={
            "question": question,
            "answer": "Inspect pod events and logs.",
            "status": "success",
            "analysis_status": "success",
            "analysis": {
                "summary": "Kubernetes pod restart investigation.",
                "severity": "unknown",
                "probable_cause": "Not confirmed",
                "evidence": ["1. Inspect pod events."],
                "recommended_actions": [item.description for item in recommendations],
                "requires_human_approval": False,
            },
            "sources": [recommendations[0].source.model_dump()],
            "action_recommendations": [item.model_dump() for item in recommendations],
            "tool_result": {"internal": "must not be exposed"},
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
    actions = data["action_recommendations"]

    assert len(actions) == 2

    assert {item["action_id"] for item in actions} == {
        "inspect_pod",
        "read_logs",
    }

    assert all(item["execution_status"] == "not_executed" for item in actions)

    assert all(item["requires_human_approval"] is False for item in actions)

    assert all(
        item["source"]["document_key"] == "runbooks/kubernetes-pod-runbook.md"
        for item in actions
    )

    assert "tool_result" not in data


def test_rejected_question_has_no_recommendations(monkeypatch):
    mock_invoke = AsyncMock(
        return_value={
            "status": "rejected",
            "answer": "No appropriate operational tool.",
        }
    )

    monkeypatch.setattr(
        agent_route,
        "agent_graph",
        SimpleNamespace(ainvoke=mock_invoke),
    )

    response = client.post(
        URL, headers=HEADERS, json={"question": "What is the company's annual revenue?"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "rejected"
    assert data["analysis"] is None
    assert data["action_recommendations"] == []
