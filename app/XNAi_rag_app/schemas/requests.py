"""
Xoe-NovAi Request Schemas
=========================
Pydantic models for API requests.
"""

from typing import Optional, List
from pydantic import BaseModel, Field

class LoginRequest(BaseModel):
    username: str
    password: str
    mfa_code: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class CreateUserRequest(BaseModel):
    username: str
    email: str
    full_name: str
    password: str

class QueryRequest(BaseModel):
    """
    Query request model.
    """
    query: str = Field(
        ..., 
        min_length=1, 
        max_length=2000, 
        description="User query",
        examples=["What is Xoe-NovAi?"]
    )
    use_rag: bool = Field(
        True, 
        description="Whether to use RAG context retrieval"
    )
    max_tokens: int = Field(
        512, 
        ge=1, 
        le=2048, 
        description="Maximum tokens to generate"
    )
    temperature: float = Field(
        0.7, 
        ge=0.0, 
        le=2.0, 
        description="Sampling temperature"
    )
    top_p: float = Field(
        0.95,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
