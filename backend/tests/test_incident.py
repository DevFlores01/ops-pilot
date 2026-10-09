import pytest

from pydantic import ValidationError

from app.models.incident import IncidentAnalysis

def test_valid_incident():
    incident = IncidentAnalysis(
        summary="Payment API failure",
        severity="high",
        probable_cause="Database connection exhaustion",
        evidence=["PostgreSQL connection error"],
        recommended_actions=["Inspect active connections"],
        requires_human_approval=False
    )
    
    assert incident.severity == "high"
    assert len(incident.evidence) == 1
    
def test_invalid_serverity():
    with pytest.raises(ValidationError):
        IncidentAnalysis(
            summary="Payment API failure",
            severity="extreme",
            probable_cause="Unknown",
            evidence=[],
            recommended_actions=[],
            requires_human_approval=False
        )
        
def test_missing_required_field():
    with pytest.raises(ValidationError):
        IncidentAnalysis(
            summary="Payment API failure",
            severity="high",
            probable_cause="Unknown",
            evidence=[],
            recommended_actions=[]
        )