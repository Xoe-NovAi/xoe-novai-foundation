# OpenPipe Integration Implementation Guide
## Step-by-Step Deployment for XNAi Foundation

**Version**: 1.0  
**Date**: February 21, 2026  
**Estimated Implementation Time**: 2-3 weeks

## Overview

This guide provides detailed instructions for implementing OpenPipe integration with your XNAi Foundation stack. The implementation follows a phased approach to ensure stability and maintain sovereignty.

## Prerequisites

### Environment Requirements
- **Docker/Podman**: Rootless container runtime
- **Redis**: Already deployed (v7.1.1)
- **PostgreSQL**: Already deployed (v14+)
- **VictoriaMetrics**: Already deployed
- **OpenRouter API Key**: Already configured

### Configuration Files Needed
- `config/openpipe-config.yaml` ✅ Created
- `app/XNAi_rag_app/core/openpipe_integration.py` ✅ Created
- `app/XNAi_rag_app/core/services_init_enhanced.py` ✅ Created
- `monitoring/grafana/dashboards/openpipe-dashboard.json` ✅ Created

## Phase 1: Core Infrastructure (Days 1-3)

### Step 1.1: Environment Setup

```bash
# Create OpenPipe directories
mkdir -p config/openpipe
mkdir -p data/openpipe
mkdir -p logs/openpipe

# Set proper permissions for rootless Podman
sudo chown -R $USER:$USER config/openpipe data/openpipe logs/openpipe
sudo chmod -R 755 config/openpipe
sudo chmod -R 755 data/openpipe
sudo chmod -R 755 logs/openpipe
```

### Step 1.2: Environment Variables

Add to your `.env` file:
```bash
# OpenPipe Configuration
OPENPIPE_API_KEY=your_openpipe_api_key_here
OPENPIPE_BASE_URL=http://openpipe:3000
OPENPIPE_CACHE_TTL=300
OPENPIPE_DEDUPLICATION_WINDOW=60
OPENPIPE_SOVEREIGN_MODE=true
```

### Step 1.3: Docker Compose Update

Update your `docker-compose.yml` to include the OpenPipe service (add to existing file):

```yaml
# Add this service to your existing docker-compose.yml
openpipe:
  image: openpipe/observability:latest
  container_name: xnai_openpipe
  init: true
  user: "${APP_UID:-1001}:${APP_GID:-1001}"
  deploy:
    resources:
      limits:
        memory: 1G
        cpus: '0.5'
      reservations:
        memory: 512M
        cpus: '0.25'
  ports:
    - "3000:3000"
  volumes:
    - ./config/openpipe:/app/config:Z,U
    - ./data/openpipe:/app/data:Z,U
    - ./logs/openpipe:/app/logs:Z,U
  environment:
    - OPENPIPE_API_KEY=${OPENPIPE_API_KEY}
    - REDIS_URL=redis://redis:6379
    - DATABASE_URL=postgresql://postgres:password@postgres:5432/xnai
    - CACHE_TTL=${OPENPIPE_CACHE_TTL}
    - DEDUPLICATION_WINDOW=${OPENPIPE_DEDUPLICATION_WINDOW}
    - METRICS_ENABLED=true
    - SOVEREIGN_MODE=${OPENPIPE_SOVEREIGN_MODE}
  networks:
    - xnai_network
  healthcheck:
    test: ["CMD", "wget", "-q", "--spider", "http://localhost:3000/health"]
    interval: 30s
    timeout: 10s
    retries: 3
    start_period: 30s
  restart: unless-stopped
```

### Step 1.4: Configuration File Setup

Copy the configuration file:
```bash
cp config/openpipe-config.yaml config/openpipe/config.yaml
```

## Phase 2: Code Integration (Days 4-7)

### Step 2.1: Update Main Application Entry Point

Update `app/XNAi_rag_app/api/entrypoint.py`:

```python
"""
Enhanced API Entry Point with OpenPipe Integration
==================================================
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .routes import router as api_router
from .healthcheck import router as health_router
from .metrics import router as metrics_router
from .auth import router as auth_router
from .config_loader import load_config
from .logging_config import setup_logging
from .observability import observability
from .metrics import start_metrics_server
from .circuit_breakers import initialize_circuit_breakers, initialize_voice_circuit_breakers
from .dependencies import (
    get_redis_client,
    get_http_client,
    get_embeddings,
    get_vectorstore,
    shutdown_dependencies
)
from .openpipe_integration import openpipe_manager
from .consul_client import consul_client

# Import enhanced orchestrator
from .core.services_init_enhanced import enhanced_orchestrator

logger = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Enhanced lifespan manager with OpenPipe integration."""
    global logger
    
    try:
        # 1. Configuration & Logging
        config = load_config()
        setup_logging()
        logger = app.state.logger = get_logger(__name__)
        
        # 2. Metrics & Observability
        start_metrics_server()
        
        # 3. Consul Registration
        service_id = f"rag-api-{socket.gethostname()}"
        port = config.get('api', {}).get('port', 8000)
        hostname = socket.gethostname()
        
        await consul_client.register_service(
            name="rag-api",
            service_id=service_id,
            address=hostname,
            port=port,
            check_url=f"http://{hostname}:{port}/health"
        )
        
        # 4. Circuit Breakers
        redis_url = f"redis://:{config.get('redis', {}).get('password', '')}@{config.get('redis', {}).get('host', 'redis')}:{config.get('redis', {}).get('port', 6379)}/0"
        await initialize_circuit_breakers(redis_url)
        await initialize_voice_circuit_breakers(redis_url)
        
        # 5. OpenPipe Integration
        openpipe_success = await openpipe_manager.initialize()
        if openpipe_success:
            logger.info("✓ OpenPipe integration initialized")
        else:
            logger.warning("⚠ OpenPipe integration failed, continuing without OpenPipe")
        
        # 6. Core Infrastructure
        app.state.redis = get_redis_client()
        app.state.http_client = get_http_client()
        
        # 7. Enhanced Service Initialization
        services = await enhanced_orchestrator.initialize_all()
        app.state.services = services
        
        logger.info("✓ Enhanced XNAi Foundation stack initialized with OpenPipe")
        
        yield
        
    except Exception as e:
        logger.critical(f"Failed to initialize enhanced stack: {e}", exc_info=True)
        raise
    finally:
        # Cleanup
        await enhanced_orchestrator.shutdown_all()
        await openpipe_manager.shutdown()
        await shutdown_dependencies()
        await consul_client.deregister_service(service_id)

def create_app() -> FastAPI:
    """Create FastAPI app with enhanced OpenPipe integration."""
    app = FastAPI(
        title="XNAi Foundation API",
        description="Enhanced RAG API with OpenPipe integration",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Routes
    app.include_router(api_router, prefix="/api/v1")
    app.include_router(health_router, prefix="/health")
    app.include_router(metrics_router, prefix="/metrics")
    app.include_router(auth_router, prefix="/auth")
    
    return app

app = create_app()