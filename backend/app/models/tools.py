from pydantic import BaseModel, Field


class RunbookSearchRequest(BaseModel):
    query: str = Field(
        min_length=1,
        max_length=2000,
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=5,
    )
