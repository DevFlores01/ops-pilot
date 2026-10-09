import logging

import httpx

from fastapi import APIRouter, HTTPException
from pydantic import ValidationError

from app.models.chat import ChatRequest
from app.models.incident import IncidentAnalysis
from app.services.incident_service import IncidentService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Incident Analysis"]
)

@router.post("", response_model=IncidentAnalysis)
async def analyze_incident(
    request: ChatRequest
) -> IncidentAnalysis:
    
    try:
        service = IncidentService()
        return await service.analyze(request.message)
    
    except (httpx.HTTPError, ValidationError):
        logger.exception("Incident analysis failed")
        raise HTTPException(
            status_code=502,
            detail="Incident analysis provider failed"
        )
        
    except ValueError:
        logger.exception("Incident analaysis configuration failed")
        raise HTTPException(
            status_code=500,
            detail="Incident analysis configuration error"
        )