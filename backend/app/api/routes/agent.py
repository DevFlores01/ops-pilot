import logging

from fastapi import APIRouter, Depends, HTTPException

from app.agents.graph import agent_graph
from app.core.security import require_api_key
from app.models.agent import AgentInvestigationRequest, AgentInvestigationResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/agent",
    tags=["AI Agent"],
    dependencies=[Depends(require_api_key)],
)


@router.post(
    "/investigate",
    response_model=AgentInvestigationResponse,
)
async def investigate(
    request: AgentInvestigationRequest,
) -> AgentInvestigationResponse:

    try:
        state = await agent_graph.ainvoke(
            {"question": request.question},
            config={"recursion_limit": 10},
        )

        return AgentInvestigationResponse(
            question=request.question,
            answer=state.get(
                "answer",
                "No investigation answer available.",
            ),
            status=state.get("status", "error"),
            analysis_status=state.get("analysis_status"),
            analysis=state.get("analysis"),
            sources=state.get("sources") or [],
            action_recommendations=state.get("action_recommendations") or [],
        )

    except Exception as exc:
        logger.exception("Agent investigation request failed")

        raise HTTPException(
            status_code=502,
            detail="AI agent investigation failed",
        ) from exc
