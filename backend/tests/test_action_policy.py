from app.agents.approval_policy import evaluate_action


def test_read_only_action_permitted():
    result = evaluate_action("inspect_pod")

    assert result.permitted is True
    assert result.requires_human_approval is False


def test_restart_requires_approval():
    result = evaluate_action("restart_service")

    assert result.permitted is False
    assert result.requires_human_approval is True


def test_rollback_requires_approval():
    result = evaluate_action("rollback_deployment")

    assert result.permitted is False
    assert result.requires_human_approval is True


def test_unknown_action_denied():
    result = evaluate_action("execute_shell_command")

    assert result.permitted is False
    assert result.reason == "Unknown action denied"
