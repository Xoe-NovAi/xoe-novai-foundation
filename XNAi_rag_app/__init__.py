# Compatibility shim to allow `import XNAi_rag_app.*` when source lives in `app/XNAi_rag_app`
# This keeps tests and external imports stable during refactors without moving files.
import os

__all__ = []

# Prefer the sibling `app/XNAi_rag_app` location
_shim_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'app', 'XNAi_rag_app'))
if os.path.isdir(_shim_path):
    __path__.insert(0, _shim_path)
else:
    # fallback: allow direct import if package is already present
    _alt = os.path.normpath(os.path.join(os.path.dirname(__file__), 'app', 'XNAi_rag_app'))
    if os.path.isdir(_alt):
        __path__.insert(0, _alt)
