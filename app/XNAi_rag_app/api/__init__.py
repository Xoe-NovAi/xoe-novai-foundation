"""
Xoe-NovAi API Module
====================
FastAPI application and route definitions.
"""

from fastapi import FastAPI

# Do NOT import routers here - causes circular dependencies during testing
# Instead, import in entrypoint.py when actually needed

# Export the FastAPI app instance directly
# This assumes the main FastAPI app is initialized in entrypoint.py
# and that this __init__.py is in a location where it can be imported
# by the entrypoint script (e.g., if app.py is in the root directory).

# If the app instance is named 'app' in entrypoint.py, and entrypoint.py
# is the main file, we might not need to explicitly export it here if
# the entrypoint is run directly. However, for modularity and clarity,
# it's good practice to have a clear export.

# We will export the router to be included in the main app setup.
__all__ = []

# Note: The FastAPI app instance itself is typically created in the main
# application file (e.g., entrypoint.py or main.py) and not directly
# exported from __init__.py in this structure. The router is included
# in the main app setup.