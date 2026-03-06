"""
Xoe-NovAi Package Initialization
=================================
Establishes consistent import paths for all modules.

Pattern: Environment-based path resolution (2024 best practice)
"""

import os
import sys
from pathlib import Path

# Version - Updated by semantic-release
__version__ = "0.2.0"


def setup_import_paths():
    """
    Configure Python import paths using environment-based resolution.

    This function should be called ONCE at package initialization.
    All subsequent imports use package-relative patterns.

    Research Source: Python Packaging Guide 2024
    Best Practice: Environment variables > hardcoded paths
    """
    # Get project root from environment or auto-detect
    project_root = os.getenv("XOE_NOVAI_ROOT", str(Path(__file__).parent.parent.parent.absolute()))

    # Add to sys.path only if not already present
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    # Set environment variable for child processes
    os.environ.setdefault("XOE_NOVAI_ROOT", project_root)

    return project_root


# Initialize paths on package import
_PROJECT_ROOT = setup_import_paths()

# Export for use in other modules
__all__ = ["_PROJECT_ROOT", "__version__"]
