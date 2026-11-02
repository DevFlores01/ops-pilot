import logging

from langgraph.graph import END, START, StateGraph

from app.agents.decision_service import DecisionService
from app.agents.state import AgentState
from app.services.mcp_client_service import MCPClientService
from app.agents.response_service import ResponseService
from app.agents.evidence_policy import validate_sources
from app.agents.structured_incident_service import StructuredIncidentService
from app.agents.evidence_validator import (
    EvidenceValidationError,
    validate_incident_evidence,
)

logger = logging.getLogger(__name__)

ALLOWED_TOOLS = {
    "search_runbooks",
    "list_runbooks",
}

MIN_SIMILARITY = 0.55


async def decide_node(state: AgentState) -> dict:
    decision = await DecisionService().decide(state["question"])

    tool = decision.tool

    if tool not in ALLOWED_TOOLS:
        return {
            "selected_tool": "none",
            "tool_arguments": {},
            "status": "rejected",
        }

    if tool == "search_runbooks":
        arguments = {
            # Use the original user question, not model-generated arbitrary arguments.
            "query": state["question"],
            "top_k": 3,
        }
    else:
        arguments = {}

    return {
        "selected_tool": tool,
        "tool_arguments": arguments,
        "status": "approved",
    }


def route_after_decision(state: AgentState) -> str:
    if state["status"] == "approved":
        return "execute_tool"

    return "finish_without_tool"


async def execute_tool_node(state: AgentState) -> dict:
    service = MCPClientService()

    try:
        result = await service.call_tool(
            state["selected_tool"],
            arguments=state["tool_arguments"],
        )

        return {
            "tool_result": result,
            "status": "tool_success",
        }

    except Exception:
        logger.exception("Agent MCP tool failed")

        return {
            "tool_result": None,
            "status": "tool_error",
        }


def finish_without_tool_node(state: AgentState) -> dict:
    return {
        "answer": (
            "I cannot use the available operational " "tools to answer this request."
        ),
        "status": "rejected",
    }


def finish_with_tool_node(state: AgentState) -> dict:
    if state["status"] == "tool_error":
        return {
            "answer": (
                "The operational tool is currently "
                "unavailable. No infrastructure "
                "changes were performed."
            ),
        }

    result = state.get("tool_result")

    if not result:
        return {
            "answer": ("No operational evidence was returned."),
            "status": "insufficient_context",
        }

    return {
        "answer": (
            "The operational tool returned evidence. "
            "Review the structured tool_result field "
            "for the retrieved runbook information."
        ),
    }


async def generate_answer_node(state: AgentState) -> dict:
    if state["status"] == "tool_error":
        return {
            "answer": (
                "The operational tool is unavailable. "
                "No infrastructure changes were performed."
            ),
            "status": "tool_error",
        }

    tool_result = state.get("tool_result") or {}

    if not isinstance(tool_result, dict):
        return {
            "answer": "Unexpected MCP response format.",
            "status": "tool_error",
        }

    results = tool_result.get("result", [])

    if not isinstance(results, list):
        return {
            "answer": "Unexpected MCP result structure.",
            "status": "tool_error",
        }

    if state["selected_tool"] == "list_runbooks":
        runbooks = [key for key in results if isinstance(key, str)]

        return {
            "answer": (
                "Available operational runbooks:\n"
                + "\n".join(f"- {key}" for key in runbooks)
                if runbooks
                else "No runbooks were found."
            ),
            "status": ("success" if runbooks else "insufficient_context"),
        }

    # This first version uses a relevance threshold.
    # We will calibrate it against evaluation data.

    evidence = [
        item
        for item in results
        if isinstance(item, dict)
        and isinstance(item.get("document_key"), str)
        and bool(item["document_key"].strip())
        and type(item.get("chunk_index")) is int
        and item["chunk_index"] >= 0
        and isinstance(item.get("content"), str)
        and bool(item["content"].strip())
        and type(item.get("similarity")) in (int, float)
        and MIN_SIMILARITY <= item["similarity"] <= 1.0
    ][:3]

    if not evidence:
        return {
            "answer": (
                "Insufficient relevant operational evidence " "to answer this question."
            ),
            "status": "insufficient_context",
        }

    sources = validate_sources(evidence)

    if not sources:
        return {
            "answer": "No valid evidence sources were found.",
            "sources": [],
            "status": "insufficient_context",
        }

    try:
        generated = await ResponseService().generate(
            question=state["question"],
            evidence=evidence,
        )

    except Exception:
        logger.exception("Agent answer generation failed")
        return {
            "answer": "Unable to generate an incident analysis.",
            "status": "generation_error",
        }

    return {
        "answer": generated.answer,
        "sources": sources,
        "status": "success",
    }


def build_agent_graph():
    graph = StateGraph(AgentState)

    graph.add_node("decide", decide_node)
    graph.add_node("execute_tool", execute_tool_node)

    graph.add_node(
        "finish_without_tool",
        finish_without_tool_node,
    )

    graph.add_node("generate_answer", generate_answer_node)

    graph.add_node(
        "structured_analysis",
        structured_analysis_node,
    )

    graph.add_edge(START, "decide")

    graph.add_conditional_edges(
        "decide",
        route_after_decision,
        {
            "execute_tool": "execute_tool",
            "finish_without_tool": "finish_without_tool",
        },
    )

    graph.add_edge("execute_tool", "generate_answer")

    graph.add_conditional_edges(
        "generate_answer",
        route_after_answer,
        {"structured_analysis": "structured_analysis", "end": END},
    )

    graph.add_edge("structured_analysis", END)

    graph.add_edge("finish_without_tool", END)

    return graph.compile()


def route_after_answer(state: AgentState) -> str:
    if (
        state.get("status") == "success"
        and state.get("selected_tool") == "search_runbooks"
    ):
        return "structured_analysis"

    return "end"


async def structured_analysis_node(
    state: AgentState,
) -> dict:
    """Generate structured analysis from validated MCP evidence."""

    # Only analyzed successful runbook searches.
    if (
        state.get("status") != "success"
        or state.get("selected_tool") != "search_runbooks"
    ):
        return {
            "analysis": None,
            "analysis_status": "skipped",
        }

    tool_result = state.get("tool_result")

    if not isinstance(tool_result, dict):
        return {
            "analysis": None,
            "analysis_status": "invalid_tool_result",
        }

    results = tool_result.get("result")

    if not isinstance(results, list):
        return {
            "analysis": None,
            "analysis_status": "invalid_tool_result",
        }

    evidence = [
        item
        for item in results
        if isinstance(item, dict)
        and isinstance(item.get("document_key"), str)
        and bool(item["document_key"].strip())
        and type(item.get("chunk_index")) is int
        and item["chunk_index"] >= 0
        and isinstance(item.get("content"), str)
        and bool(item["content"].strip())
        and type(item.get("similarity")) in (int, float)
        and MIN_SIMILARITY <= item["similarity"] <= 1.0
    ][:3]

    if not evidence:
        return {
            "analysis": None,
            "analysis_status": "insufficient_evidence",
        }

    try:
        # Validate sources before sending context to Ollama.
        sources = validate_sources(evidence)

        if not sources:
            return {
                "analysis": None,
                "analysis_status": "insufficient_evidence",
            }

        # Only include evidence belonging to validated sources.
        valid_ids = {(source.document_key, source.chunk_index) for source in sources}

        evidence = [
            item
            for item in evidence
            if (
                item["document_key"],
                item["chunk_index"],
            )
            in valid_ids
        ]

        if not evidence:
            return {
                "analysis": None,
                "analysis_status": "insufficient_evidence",
            }

        incident = await StructuredIncidentService().generate(
            question=state["question"],
            evidence=evidence,
        )

        # print("GENERATED INCIDENT EVIDENCE:", incident.evidence)

        # Validate AI generated evidence against the actual retrieved runbook content.
        validated_incident = validate_incident_evidence(
            incident,
            evidence,
        )

        return {
            "analysis": validated_incident.model_dump(),
            "analysis_status": "success",
            "sources": sources,
        }

    except EvidenceValidationError:
        logger.warning("Structured incident evidence validation failed")

        return {
            "analysis": None,
            "analysis_status": "invalid_evidence",
        }

    except Exception:
        logger.exception("Structured agent analysis failed")

        return {
            "analysis": None,
            "analysis_status": "generation_error",
        }


agent_graph = build_agent_graph()
