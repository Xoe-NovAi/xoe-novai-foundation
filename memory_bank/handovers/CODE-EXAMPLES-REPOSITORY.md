---
title: Code Examples Repository
author: Copilot CLI (Copy-Paste Ready)
date: 2026-02-25T23:59:00Z
version: 1.0
token_cost: 1500
---

# 💻 CODE EXAMPLES REPOSITORY

**Purpose**: Copy-paste ready code snippets for Phase 1-5 implementation  
**Token cost**: 1,500 tokens (read once, reference as needed)

---

## ✅ PortableService Base Class

```python
# File: app/XNAi_rag_app/core/portable_service.py

from typing import Optional, Dict, Any
import logging
from abc import ABC, abstractmethod
import asyncio

logger = logging.getLogger(__name__)

class PortableService(ABC):
    """Base class for all Foundation stack services"""
    
    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.is_healthy = True
        self.error_count = 0
    
    async def initialize(self) -> None:
        """Called on service startup"""
        logger.info(f"Initializing {self.name} v{self.version}")
        await self._setup()
    
    async def shutdown(self) -> None:
        """Called on service shutdown (graceful)"""
        logger.info(f"Shutting down {self.name}")
        await self._cleanup()
        logger.info(f"Shutdown complete for {self.name}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Return health status"""
        return {
            "name": self.name,
            "version": self.version,
            "healthy": self.is_healthy,
            "error_count": self.error_count
        }
    
    @abstractmethod
    async def _setup(self) -> None:
        """Override to setup service resources"""
        pass
    
    @abstractmethod
    async def _cleanup(self) -> None:
        """Override to cleanup service resources"""
        pass
```

---

## ✅ XNAiException Hierarchy

```python
# File: app/XNAi_rag_app/core/exceptions.py

import json
from typing import Optional, Dict, Any

class XNAiException(Exception):
    """Base exception for all XNAi errors"""
    
    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN",
        context: Optional[Dict[str, Any]] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None
    ):
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.trace_id = trace_id
        self.span_id = span_id
        super().__init__(message)
    
    def to_json(self) -> str:
        """Return JSON representation for logging"""
        return json.dumps({
            "error": self.error_code,
            "message": self.message,
            "context": self.context,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        })

class ServiceUnavailableError(XNAiException):
    """Service is temporarily unavailable"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "SERVICE_UNAVAILABLE", **kwargs)

class ValidationError(XNAiException):
    """Input validation failed"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "VALIDATION_ERROR", **kwargs)

class RateLimitError(XNAiException):
    """Rate limit exceeded"""
    def __init__(self, message: str, **kwargs):
        super().__init__(message, "RATE_LIMIT", **kwargs)
```

---

## ✅ Health Check Endpoint

```python
# File: app/XNAi_rag_app/api/health.py

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio

router = APIRouter(prefix="/health", tags=["health"])

@router.get("")
async def aggregate_health() -> Dict[str, Any]:
    """Get aggregate health of all services"""
    # Import all services
    from app.XNAi_rag_app.services import (
        voice_module, llm_router, session_manager, knowledge_client
    )
    
    services = [voice_module, llm_router, session_manager, knowledge_client]
    health_checks = await asyncio.gather(
        *[s.health_check() for s in services],
        return_exceptions=True
    )
    
    overall_healthy = all(h.get("healthy") for h in health_checks if isinstance(h, dict))
    
    return {
        "status": "healthy" if overall_healthy else "degraded",
        "services": health_checks
    }

@router.get("/{service_name}")
async def service_health(service_name: str) -> Dict[str, Any]:
    """Get health of specific service"""
    from app.XNAi_rag_app.services import get_service
    
    service = get_service(service_name)
    if not service:
        raise HTTPException(status_code=404, detail="Service not found")
    
    return await service.health_check()
```

---

## ✅ Graceful Shutdown Handler

```python
# File: app/XNAi_rag_app/core/shutdown.py

import signal
import asyncio
import logging
from typing import Callable, List

logger = logging.getLogger(__name__)

class GracefulShutdownHandler:
    def __init__(self, app, timeout_seconds: int = 30):
        self.app = app
        self.timeout = timeout_seconds
        self.cleanup_tasks: List[Callable] = []
    
    def register_cleanup(self, task: Callable) -> None:
        """Register a cleanup task to run on shutdown"""
        self.cleanup_tasks.append(task)
    
    async def handle_shutdown(self) -> None:
        """Execute graceful shutdown"""
        logger.info("Starting graceful shutdown...")
        
        try:
            # Run all cleanup tasks with timeout
            cleanup_coros = [task() for task in self.cleanup_tasks]
            await asyncio.wait_for(
                asyncio.gather(*cleanup_coros, return_exceptions=True),
                timeout=self.timeout
            )
            logger.info("Graceful shutdown complete")
        except asyncio.TimeoutError:
            logger.error(f"Shutdown timeout after {self.timeout}s")

def setup_shutdown_handler(app) -> GracefulShutdownHandler:
    """Setup signal handlers for graceful shutdown"""
    handler = GracefulShutdownHandler(app)
    
    async def signal_handler(sig):
        logger.info(f"Received signal {sig}")
        await handler.handle_shutdown()
    
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(signal_handler(s)))
    
    return handler
```

---

## ✅ Feature Flag Implementation

```python
# File: app/XNAi_rag_app/core/feature_flags.py

import os
from typing import Dict
import json

class FeatureFlags:
    """Runtime-toggleable feature flags"""
    
    DEFAULTS = {
        "FEATURE_VOICE": os.getenv("FEATURE_VOICE", "false").lower() == "true",
        "FEATURE_REDIS": os.getenv("FEATURE_REDIS", "true").lower() == "true",
        "FEATURE_QDRANT": os.getenv("FEATURE_QDRANT", "true").lower() == "true",
        "FEATURE_LOCAL_FALLBACK": os.getenv("FEATURE_LOCAL_FALLBACK", "true").lower() == "true",
    }
    
    def __init__(self):
        self._flags = self.DEFAULTS.copy()
    
    def is_enabled(self, flag_name: str) -> bool:
        """Check if feature is enabled"""
        return self._flags.get(flag_name, False)
    
    def toggle(self, flag_name: str) -> bool:
        """Toggle feature flag, return new value"""
        if flag_name not in self._flags:
            raise ValueError(f"Unknown flag: {flag_name}")
        self._flags[flag_name] = not self._flags[flag_name]
        return self._flags[flag_name]
    
    def set(self, flag_name: str, value: bool) -> None:
        """Set feature flag explicitly"""
        if flag_name not in self._flags:
            raise ValueError(f"Unknown flag: {flag_name}")
        self._flags[flag_name] = value
    
    def to_json(self) -> str:
        """Return JSON representation"""
        return json.dumps(self._flags)

# Global instance
flags = FeatureFlags()
```

---

## ✅ Blue-Green Deployment Pattern

```bash
#!/bin/bash
# File: scripts/deploy-blue-green.sh

set -e

BLUE_PORT=8000
GREEN_PORT=8001

echo "Starting GREEN environment on port $GREEN_PORT..."
docker-compose up -d --scale green=1

echo "Running smoke tests on GREEN..."
sleep 5  # Wait for service to start
curl -f http://localhost:$GREEN_PORT/health || exit 1

echo "Load balancer: switching to GREEN..."
# Update nginx/load balancer config to route to GREEN
sed -i "s/server.*:$BLUE_PORT/server 127.0.0.1:$GREEN_PORT/" /etc/nginx/nginx.conf
nginx -s reload

echo "Monitoring GREEN for 5 minutes..."
for i in {1..30}; do
    sleep 10
    curl -f http://localhost:$GREEN_PORT/health || {
        echo "GREEN health check failed, rolling back!"
        sed -i "s/server.*:$GREEN_PORT/server 127.0.0.1:$BLUE_PORT/" /etc/nginx/nginx.conf
        nginx -s reload
        exit 1
    }
done

echo "Deployment successful! GREEN is now production."
docker-compose down  # Stop old BLUE containers
```

---

## Summary Table

| Code Example | Purpose | File | Tokens |
|--------------|---------|------|--------|
| PortableService | Service base class | `core/portable_service.py` | 300 |
| XNAiException | Unified error handling | `core/exceptions.py` | 200 |
| Health Check | Service health endpoint | `api/health.py` | 250 |
| Graceful Shutdown | Clean exit handling | `core/shutdown.py` | 250 |
| Feature Flags | Runtime toggles | `core/feature_flags.py` | 200 |
| Blue-Green Deploy | Zero-downtime deployment | `scripts/deploy-blue-green.sh` | 200 |

**Total**: ~1,500 tokens (6 examples, copy-paste ready)

---

**Document**: CODE-EXAMPLES-REPOSITORY.md  
**Purpose**: Copy-paste implementation snippets  
**Token cost**: 1,500 (read once, reference as needed)  
**Status**: ✅ Ready for Phase 1-5 implementation
