"""
Xoe-NovAi Response Schemas
==========================
Pydantic models for API responses.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: Dict[str, Any]

class QueryResponse(BaseModel):
    """
    Query response model.
    """
    response: str = Field(..., description="Generated response")
    sources: List[str] = Field(default_factory=list, description="RAG sources used")
    tokens_generated: Optional[int] = Field(None, description="Number of tokens generated")
    duration_ms: Optional[float] = Field(None, description="Processing time in milliseconds")
    token_rate_tps: Optional[float] = Field(None, description="Tokens per second")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Health status: healthy, degraded, or partial")
    version: str = Field(..., description="Stack version")
    memory_gb: float = Field(..., description="Current memory usage in GB")
    vectorstore_loaded: bool = Field(..., description="Whether vectorstore is available")
    components: Dict[str, bool] = Field(..., description="Component status map")
