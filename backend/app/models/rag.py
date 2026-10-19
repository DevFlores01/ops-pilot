from pydantic import BaseModel, Field

class RAGRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    top_k: int = Field(default=3, ge=1, le=20)
    
class RAGSource(BaseModel):
    document_key: str
    chunk_index: int
    similarity: float
    content: str
    
class RAGResponse(BaseModel):
    question: str
    answer: str
    sources: list[RAGSource]
    status: str