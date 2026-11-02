from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SourceReference(BaseModel):
    model_config = ConfigDict(extra="forbid")

    document_key: str = Field(min_length=1)
    chunk_index: int = Field(ge=0)
    similarity: float = Field(ge=0.0, le=1.0)


class StructuredIncident(BaseModel):
    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1)
    severity: Literal[
        "unknown",
        "low",
        "medium",
        "high",
        "critical",
    ] = "unknown"
    probable_cause: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    requires_human_approval: bool = False
