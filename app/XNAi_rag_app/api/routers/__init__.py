"""
Xoe-NovAi API Routers
====================
Register all API routers here.
"""

from fastapi import APIRouter
from XNAi_rag_app.api.routers.health import router as health_router
from XNAi_rag_app.api.routers.query import router as query_router

router = APIRouter()

router.include_router(health_router, tags=["health"])
router.include_router(query_router, tags=["query"])
