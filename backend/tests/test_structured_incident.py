import json
from unittest.mock import AsyncMock, Mock

import httpx
import pytest

from app.agents.structured_incident_service import (
    StructuredIncidentService,
    StructuredIncidentError,
)

EVIDENCE = [
    {
        "document_key": "runbooks/kubernetes-pod-runbook.md",
        "chunk_index": 0,
        "similarity": 0.7862,
        "content": "Inspect pod events and container logs.",
    }
]


@pytest.mark.asyncio
async def test_valid_structured_incident(monkeypatch):
    incident = {
        "summary": "Kubernetes pod is restarting.",
        "severity": "unknown",
        "probable_cause": "Not confirmed.",
        "evidence": ["Inspect pod events."],
        "recommended_actions": ["Review container logs."],
        "requires_human_approval": False,
    }

    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"message": {"content": json.dumps(incident)}}

    client = AsyncMock()
    client.post.return_value = response

    context = AsyncMock()
    context.__aenter__.return_value = client

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: context,
    )

    service = StructuredIncidentService()

    result = await service.generate(
        "Why is my pod restarting?",
        EVIDENCE,
    )

    assert result.severity == "unknown"
    assert result.summary == incident["summary"]


@pytest.mark.asyncio
async def test_invalid_json_rejected(monkeypatch):
    response = Mock()
    response.raise_for_status = Mock()
    response.json.return_value = {"message": {"content": "This is not JSON"}}

    client = AsyncMock()
    client.post.return_value = response

    context = AsyncMock()
    context.__aenter__.return_value = client

    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda **kwargs: context,
    )

    service = StructuredIncidentService()

    with pytest.raises(StructuredIncidentError):
        await service.generate(
            "Why is my pod restarting?",
            EVIDENCE,
        )


@pytest.mark.asyncio
async def test_empty_evidence_rejected():
    service = StructuredIncidentService()

    with pytest.raises(ValueError):
        await service.generate(
            "Why is my pod restarting?",
            [],
        )
