"""
Xoe-NovAi API Routers
====================
Register all API routers here.
"""

from fastapi import APIRouter
from .health import router as health_router
from .query import router as query_router
from .websocket import router as websocket_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(query_router, tags=["query"])
router.include_router(websocket_router, tags=["websocket"])