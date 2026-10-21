import logging

from fastapi import APIRouter, HTTPException, Depends

from app.models.tools import RunbookSearchRequest
from app.services.mcp_client_service import MCPClientService
from app.core.security import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/tools",
    tags=["MCP Tools"],
    dependencies=[Depends(require_api_key)],
)


@router.get("/runbooks")
async def list_runbooks():
    try:
        service = MCPClientService()

        result = await service.call_tool("list_runbooks", arguments={})

        return {
            "status": "success",
            "data": result,
        }

    except Exception:
        logger.exception("MCP runbook listing failed")
        raise HTTPException(
            status_code=502,
            detail="Unable to list runbooks",
        )


@router.post("/search")
async def search_runbooks(
    request: RunbookSearchRequest,
):
    try:
        service = MCPClientService()

        result = await service.call_tool(
            "search_runbooks",
            arguments={
                "query": request.query,
                "top_k": request.top_k,
            },
        )

        return {
            "status": "success",
            "data": result,
        }

    except Exception:
        logger.exception("MCP runbook search failed")
        raise HTTPException(status_code=502, detail="Unable to search runbooks")
