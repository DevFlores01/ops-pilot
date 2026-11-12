from app.agents.approval_policy import evaluate_action
from app.models.agent_response import ActionRecommendation, StructuredIncident


def finalize_runbook_report(
    question: str,
    incident: StructuredIncident,
    recommendations: list[ActionRecommendation],
) -> dict:
    """
    Finalize documentation-only investigations.

    Runbooks are not proof of live infrastructure state.
    Only read-only, policy-approved recommendations
    are included. No actions are executed.
    """

    safe_actions = []

    for item in recommendations:
        decision = evaluate_action(item.action_id)

        if (
            decision.permitted
            and not decision.requires_human_approval
            and item.execution_status == "not_executed"
        ):
            safe_actions.append(item.description)

    safe_actions = list(dict.fromkeys(safe_actions))

    analysis = incident.model_dump()

    analysis["summary"] = (
        "Runbook-based investigation. " "No live infrastructure has been inspected."
    )
    analysis["severity"] = "unknown"
    analysis["probable_cause"] = "Not confirmed by live observations."

    analysis["recommended_actions"] = safe_actions
    analysis["requires_human_approval"] = False

    answer = (
        f"Runbook-based guidance for: {question}\n\n"
        "The available documentation describes possible "
        "causes, not a confirmed root cause. "
        "Live investigation is required."
    )

    if safe_actions:
        answer += "\n\nSuggested read-only investigations:\n" + "\n".join(
            f"- {action}" for action in safe_actions
        )

    return {
        "answer": answer,
        "analysis": analysis,
    }
