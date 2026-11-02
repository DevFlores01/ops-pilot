import pytest

from app.agents.evidence_validator import (
    EvidenceValidationError,
    validate_incident_evidence,
)
from app.models.agent_response import StructuredIncident


def make_incident(evidence):
    return StructuredIncident(
        summary="kubernetes pod restarting",
        severity="unknown",
        probable_cause="Not confirmed",
        evidence=evidence,
        recommended_actions=["Inspect pod events"],
        requires_human_approval=False,
    )


RETRIEVED = [
    {
        "document_key": "runbooks/kubernetes-pod-runbook.md",
        "content": "Inspect pod events.",
        "similarity": 0.7862,
    }
]


def test_valid_evidence():
    incident = make_incident(["Inspect pod events."])

    result = validate_incident_evidence(
        incident,
        RETRIEVED,
    )

    assert result == incident


def test_missing_generated_evidence():
    incident = make_incident([])

    with pytest.raises(EvidenceValidationError):
        validate_incident_evidence(
            incident,
            RETRIEVED,
        )


def test_missing_retrieved_evidence():
    incident = make_incident(["Inspect pod events."])

    with pytest.raises(EvidenceValidationError):
        validate_incident_evidence(
            incident,
            [],
        )


def test_unsupported_evidence_rejected():
    incident = make_incident(
        ["The production Kubernetes cluster has lost all worker nodes."]
    )

    with pytest.raises(EvidenceValidationError):
        validate_incident_evidence(
            incident,
            RETRIEVED,
        )
