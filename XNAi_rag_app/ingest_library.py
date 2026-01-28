"""Compatibility shim: expose `XNAi_rag_app.ingest_library` from
`XNAi_rag_app.services.ingest_library` for legacy imports in tests.
"""
from XNAi_rag_app.services.ingest_library import *  # noqa: F401,F403
