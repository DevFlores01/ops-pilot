from typing import Any, TypedDict

from app.models.agent_response import SourceReference


class AgentState(TypedDict, total=False):
    question: str
    selected_tool: str
    tool_arguments: dict[str, Any]
    tool_result: Any

    answer: str
    status: str

    analysis: dict[str, Any] | None
    analysis_status: str

    sources: list[dict[str, Any]]

    action_recommendations: list[dict]
