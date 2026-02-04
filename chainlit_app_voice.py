"""Top-level shim for legacy imports expecting `chainlit_app_voice` module.
Delegates to `XNAi_rag_app.chainlit_app_voice`.
"""
from XNAi_rag_app.chainlit_app_voice import *  # noqa: F401,F403

def _session_manager():
    """Shim for legacy _session_manager function."""
    from XNAi_rag_app.chainlit_app_voice import _session_manager
    return _session_manager()
