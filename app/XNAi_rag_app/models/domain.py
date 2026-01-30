"""
Xoe-NovAi Domain Models
=======================
Core domain entities for the AI stack.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Document(BaseModel):
    """Represents a curated document in the knowledge base."""
    id: str
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

class User(BaseModel):
    """Represents a system user."""
    id: str
    username: str
    email: str
    full_name: str
    roles: List[str] = Field(default_factory=list)
    permissions: List[str] = Field(default_factory=list)
    mfa_enabled: bool = False

class Session(BaseModel):
    """Represents a user conversation session."""
    id: str
    user_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_active: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VectorIndex(BaseModel):
    """Represents a vectorstore index."""
    name: str
    path: str
    dimensions: int
    vector_count: int
    last_updated: datetime
