from typing import Literal

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
