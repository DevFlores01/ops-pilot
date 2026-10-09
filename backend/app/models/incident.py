from typing import Literal

from pydantic import BaseModel, Field

class IncidentAnalysis(BaseModel):
    summary: str = Field(
        description="Short description of the incident"
    )
    
    severity: Literal[
        "low", "medium", "high", "critical"," unkown"
    ]
    
    probable_cause: str = Field(
        description="Likely root cause or unknown"
    )
    
    evidence: list[str] = Field(
        description="Evidence supplied in the incident report"
    )
    
    recommended_actions: list[str] = Field(
        description="Suggested investigation or remediation steps"
    )
    
    requires_human_approval: bool = Field(
        description="Whether any suggested action changes system state"
    )