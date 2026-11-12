from typing import Literal
from dataclasses import dataclass

ActionType = Literal[
    "read_logs",
    "inspect_metrics",
    "inspect_pod",
    "restart_service",
    "delete_resource",
    "rollback_deployment",
    "modify_configuration",
]

READ_ONLY_ACTIONS = {
    "read_logs",
    "inspect_metrics",
    "inspect_pod",
}


def requires_approval(action: ActionType) -> bool:
    return action not in READ_ONLY_ACTIONS


@dataclass(frozen=True)
class ActionPolicyDecision:
    permitted: bool
    requires_human_approval: bool
    reason: str


READ_ONLY_OPERATIONS = {
    "read_logs",
    "inspect_metrics",
    "inspect_pod",
}

STATE_CHANGING_OPERATIONS = {
    "restart_service",
    "delete_resource",
    "rollback_deployment",
    "modify_configuration",
}


def evaluate_action(action: str) -> ActionPolicyDecision:

    if action in READ_ONLY_OPERATIONS:
        return ActionPolicyDecision(
            permitted=True,
            requires_human_approval=False,
            reason="Approved read-only action",
        )

    if action in STATE_CHANGING_OPERATIONS:
        return ActionPolicyDecision(
            permitted=False,
            requires_human_approval=True,
            reason="Human approval workflow required",
        )

    return ActionPolicyDecision(
        permitted=False,
        requires_human_approval=False,
        reason="Unknown action denied",
    )
