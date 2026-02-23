"""Top-level shim for legacy imports expecting `chainlit_app_voice` module.
Delegates to unified Chainlit app.

Updated: 2026-02-22 - Now points to unified app
"""

from XNAi_rag_app.ui.chainlit_app_unified import *  # noqa: F401,F403


# Legacy compatibility
def _session_manager():
    """Shim for legacy _session_manager function."""
    from XNAi_rag_app.core.infrastructure import create_session_manager

    return create_session_manager()
