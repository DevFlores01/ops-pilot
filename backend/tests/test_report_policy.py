from app.agents.report_policy import finalize_runbook_report
from app.agents.recommendation_policy import build_recommendations
from app.models.agent_response import (
    ActionRecommendation,
    SourceReference,
    StructuredIncident,
)

QUESTION = "Why is my Kubernetes pod in CrashLoopBackOff?"

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


def make_incident():
    return StructuredIncident(
        summary="OOMKilled caused the pod failure.",
        severity="critical",
        probable_cause="Confirmed memory exhaustion",
        evidence=["1. Inspect pod events."],
        recommended_actions=["Restart every pod"],
        requires_human_approval=False,
    )


def test_unverified_root_cause_is_not_confirmed():
    result = finalize_runbook_report(
        QUESTION,
        make_incident(),
        [],
    )

    analysis = result["analysis"]

    assert analysis["severity"] == "unknown"
    assert analysis["probable_cause"] == ("Not confirmed by live observations.")
    assert "OOMKilled" not in analysis["summary"]
    assert analysis["recommended_actions"] == []


def test_curated_read_only_actions_are_preserved():
    recommendations = build_recommendations([EVIDENCE])

    result = finalize_runbook_report(
        QUESTION,
        make_incident(),
        recommendations,
    )

    actions = result["analysis"]["recommended_actions"]

    assert len(actions) == 2
    assert len(recommendations) == 2
    assert "Inspect Kubernetes pod events." in actions
    assert "Review Kubernetes container logs." in actions
    assert result["analysis"]["requires_human_approval"] is False


def test_malicious_model_approval_flag_cannot_permit_restart():
    unsafe = ActionRecommendation(
        action_id="restart_service",
        description="Restart Kubernetes workloads.",
        source=SourceReference(
            document_key=EVIDENCE["document_key"],
            chunk_index=0,
            similarity=0.7862,
        ),
        policy_permitted=True,
        requires_human_approval=False,
        execution_status="not_executed",
    )

    result = finalize_runbook_report(
        QUESTION,
        make_incident(),
        [unsafe],
    )

    assert result["analysis"]["requires_human_approval"] is False
    assert result["analysis"]["recommended_actions"] == []
    assert "Restart Kubernetes" not in result["answer"]


def test_report_disclose_no_live_obervations():
    result = finalize_runbook_report(
        QUESTION,
        make_incident(),
        [],
    )

    assert "Live investigation is required" in result["answer"]

    assert "No live infrastructure has been inspected." in result["analysis"]["summary"]

    assert result["analysis"]["severity"] == "unknown"

    assert result["analysis"]["probable_cause"] == (
        "Not confirmed by live observations."
    )
