from dataclasses import dataclass

from app.agents.approval_policy import evaluate_action
from app.agents.evidence_policy import validate_sources
from app.models.agent_response import ActionRecommendation


@dataclass(frozen=True)
class RecommendationRule:
    document_key: str
    required_excerpt: str
    action_id: str
    description: str


RULES = (
    RecommendationRule(
        document_key="runbooks/kubernetes-pod-runbook.md",
        required_excerpt="Inspect pod events.",
        action_id="inspect_pod",
        description="Inspect Kubernetes pod events.",
    ),
    RecommendationRule(
        document_key="runbooks/kubernetes-pod-runbook.md",
        required_excerpt="Check container logs.",
        action_id="read_logs",
        description="Review Kubernetes container logs.",
    ),
    RecommendationRule(
        document_key="runbooks/redis-cache-runbook.md",
        required_excerpt="Check Redis memory usage.",
        action_id="inspect_metrics",
        description="Inspect Redis memory utilization.",
    ),
    RecommendationRule(
        document_key="runbooks/payment-api-runbook.md",
        required_excerpt="Check application logs.",
        action_id="read_logs",
        description="Inspect payment API application logs.",
    ),
)


def build_recommendations(
    retrieved: list[dict],
) -> list[ActionRecommendation]:

    valid_sources = {
        (source.document_key, source.chunk_index): source
        for source in validate_sources(retrieved)
    }

    recommendations = []
    seen = set()

    for item in retrieved:
        if not isinstance(item, dict):
            continue

        identity = (
            item.get("document_key"),
            item.get("chunk_index"),
        )

        source = valid_sources.get(identity)
        content = item.get("content")

        if source is None or not isinstance(content, str):
            continue

        for rule in RULES:
            if rule.document_key != source.document_key:
                continue

            if rule.required_excerpt.casefold() not in content.casefold():
                continue

            if rule.action_id in seen:
                continue

            decision = evaluate_action(rule.action_id)

            if not decision.permitted or decision.requires_human_approval:
                continue

            seen.add(rule.action_id)

            recommendations.append(
                ActionRecommendation(
                    action_id=rule.action_id,
                    description=rule.description,
                    source=source,
                    policy_permitted=decision.permitted,
                    requires_human_approval=(decision.requires_human_approval),
                )
            )

    return recommendations
