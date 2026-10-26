from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    selected_tool: str
    tool_arguments: dict[str, Any]
    tool_result: Any
    answer: str
    status: str
