"""
XNAi Foundation Infrastructure Layer
====================================

Core infrastructure components for session management and knowledge retrieval.
Designed for use by Chainlit UI, voice interface, and MC agent interfaces.

Components:
- SessionManager: Redis-backed session persistence with in-memory fallback
- KnowledgeClient: Unified knowledge retrieval (Qdrant + FAISS)

CLAUDE STANDARD: Uses AnyIO for structured concurrency.
TORCH-FREE: No PyTorch dependencies.

Usage:
    from XNAi_rag_app.core.infrastructure import SessionManager, KnowledgeClient

    # Session management
    session = SessionManager()
    await session.initialize()
    await session.add_interaction("user", "Hello!")

    # Knowledge retrieval
    knowledge = KnowledgeClient()
    await knowledge.initialize()
    results = await knowledge.search("What is XNAi?")
"""

from .session_manager import (
    SessionManager,
    SessionConfig,
    create_session_manager,
    get_chainlit_session_key,
)

from .knowledge_client import (
    KnowledgeClient,
    KnowledgeConfig,
    SearchResult,
    create_knowledge_client,
)

__all__ = [
    # Session Management
    "SessionManager",
    "SessionConfig",
    "create_session_manager",
    "get_chainlit_session_key",
    # Knowledge Retrieval
    "KnowledgeClient",
    "KnowledgeConfig",
    "SearchResult",
    "create_knowledge_client",
]

__version__ = "0.1.0"
