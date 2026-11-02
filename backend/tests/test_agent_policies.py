from app.agents.approval_policy import requires_approval
from app.agents.evidence_policy import validate_sources


def test_read_only_action_does_not_require_approval():
    assert requires_approval("read_logs") is False
    assert requires_approval("inspect_pod") is False


def test_destructive_actions_requires_approval():
    assert requires_approval("restart_service") is True
    assert requires_approval("delete_resource") is True
    assert requires_approval("rollback_deployment") is True


def test_valid_evidence_source():
    sources = validate_sources(
        [
            {
                "document_key": "runbooks/kubernetes-pod-runbok.md",
                "chunk_index": 0,
                "content": "Inspect pod events and logs",
                "similarity": 0.7862,
            }
        ]
    )

    assert len(sources) == 1
    assert sources[0].chunk_index == 0


def test_invalid_evidence_is_rejected():
    sources = validate_sources(
        [
            {
                "document_key": "runbooks/invalid.md",
                "chunk_index": 0,
                "content": "",
                "similarity": 0.9,
            },
            {
                "document_key": "runbooks/unrelated.md",
                "chunk_index": 0,
                "content": "Unrelated information",
                "similarity": 0.2,
            },
        ]
    )

    assert sources == []


def test_duplicate_sources_are_removed():
    item = {
        "document_key": "runbooks/kubernetes-pod-runbook.md",
        "chunk_index": 0,
        "content": "Inspect pod events.",
        "similarity": 0.7862,
    }

    assert len(validate_sources([item, item])) == 1
