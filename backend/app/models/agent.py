from pydantic import BaseModel, ConfigDict, Field
from typing import Any

from app.models.agent_response import (
    StructuredIncident,
    SourceReference,
    ActionRecommendation,
)


class AgentInvestigationRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    question: str = Field(
        min_length=5,
        max_length=2000,
    )


class AgentInvestigationResponse(BaseModel):
    question: str
    answer: str
    status: str

    analysis_status: str | None = None
    analysis: StructuredIncident | None = None

    sources: list[dict[str, Any]] = Field(default_factory=list)

    action_recommendations: list[dict[str, Any]] = Field(default_factory=list)
