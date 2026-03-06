# XNAi Foundation: Leveraging Existing Stack Services

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Integration strategy for existing infrastructure services

## Overview

This document outlines how to leverage the existing sophisticated infrastructure stack to support the modular architecture development. The XNAi Foundation already has a comprehensive infrastructure ecosystem that can be extended and adapted for modular service development.

## Current Infrastructure Analysis

### Existing Services (24 Services Total)

#### Core Infrastructure Services
- **Consul** (3 instances): Service discovery and configuration
- **Caddy** (2 instances): Load balancing and reverse proxy
- **VictoriaMetrics** (2 instances): Time-series monitoring
- **Grafana** (2 instances): Visualization and dashboards
- **Redis** (2 instances): Message bus and caching
- **PostgreSQL** (2 instances): Primary database
- **Qdrant** (2 instances): Vector database

#### Application Services
- **RAG API** (2 instances): FastAPI backend
- **UI** (2 instances): Chainlit frontend
- **Crawler** (2 instances): Content ingestion
- **Curation Worker** (2 instances): Knowledge refinement
- **MKDocs** (2 instances): Documentation
- **Vikunja** (2 instances): Project management

### Infrastructure Capabilities

#### Service Discovery and Configuration
```yaml
# Current Consul setup provides:
consul:
  service_discovery: true
  configuration_management: true
  health_checking: true
  service_mesh: true
  multi_datacenter: true
```

#### Load Balancing and Traffic Management
```yaml
# Current Caddy setup provides:
caddy:
  load_balancing: true
  health_checks: true
  ssl_termination: true
  rate_limiting: true
  path_routing: true
  websocket_support: true
```

#### Monitoring and Observability
```yaml
# Current VictoriaMetrics + Grafana setup provides:
monitoring:
  metrics_collection: true
  alerting: true
  dashboards: true
  log_aggregation: true
  distributed_tracing: true
  performance_monitoring: true
```

## Integration Strategy for Modular Services

### 1. Service Discovery Integration

#### 1.1 Consul Service Registration

```yaml
# Service registration for new modular services
services:
  rag-core:
    consul:
      service:
        name: "rag-core"
        tags:
          - "api"
          - "rag"
          - "modular"
        address: "rag-core"
        port: 8000
        check:
          http: "http://rag-core:8000/health"
          interval: "30s"
          timeout: "10s"
          deregister_critical_service_after: "1m"
  
  knowledge-mgmt:
    consul:
      service:
        name: "knowledge-mgmt"
        tags:
          - "api"
          - "knowledge"
          - "modular"
        address: "knowledge-mgmt"
        port: 8001
        check:
          http: "http://knowledge-mgmt:8001/health"
          interval: "30s"
          timeout: "10s"
          deregister_critical_service_after: "1m"
```

#### 1.2 Configuration Management

```yaml
# Consul KV structure for modular services
consul_kv_structure:
  services:
    rag-core:
      config:
        qdrant:
          host: "qdrant"
          port: 6333
          api_key: "${QDRANT_API_KEY}"
        redis:
          host: "redis"
          port: 6379
          password: "${REDIS_PASSWORD}"
        postgres:
          host: "postgres"
          port: 5432
          database: "xnai"
          user: "postgres"
          password: "${POSTGRES_PASSWORD}"
    
    knowledge-mgmt:
      config:
        document_storage:
          path: "/app/documents"
        processing:
          chunk_size: 1000
          chunk_overlap: 100
        validation:
          enabled: true
          timeout: 30
```

### 2. Load Balancing Integration

#### 2.1 Caddy Configuration for Modular Services

```caddyfile
# Caddy configuration for modular services
{
    email admin@xnai.example.com
    servers {
        protocol {
            allow_h2c
        }
    }
}

# RAG Core service load balancing
rag-core.xnai.example.com {
    reverse_proxy rag-core:8000 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
        health_timeout 10s
        health_status 200
    }
    
    @api path /api/*
    reverse_proxy @api rag-core:8000 {
        lb_policy round_robin
    }
    
    encode zstd gzip
    header {
        X-Frame-Options DENY
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
    }
}

# Knowledge Management service
knowledge.xnai.example.com {
    reverse_proxy knowledge-mgmt:8001 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
        health_timeout 10s
        health_status 200
    }
    
    encode zstd gzip
    header {
        X-Frame-Options DENY
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
    }
}

# UI Service
ui.xnai.example.com {
    reverse_proxy ui-service:3000 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
        health_timeout 10s
        health_status 200
    }
    
    encode zstd gzip
    header {
        X-Frame-Options DENY
        X-Content-Type-Options nosniff
        X-XSS-Protection "1; mode=block"
        Referrer-Policy strict-origin-when-cross-origin
    }
}
```

#### 2.2 Service Mesh Configuration

```yaml
# Consul service mesh configuration
service_mesh:
  mesh_gateway:
    enabled: true
    mode: "remote"
    wan_federation_enabled: true
  
  intentions:
    allow_all: false
    default_policy: "deny"
    rules:
      - source_service: "ui-service"
        destination_service: "rag-core"
        action: "allow"
      - source_service: "ui-service"
        destination_service: "knowledge-mgmt"
        action: "allow"
      - source_service: "knowledge-mgmt"
        destination_service: "rag-core"
        action: "allow"
      - source_service: "crawler"
        destination_service: "knowledge-mgmt"
        action: "allow"
```

### 3. Monitoring Integration

#### 3.1 VictoriaMetrics Metrics Collection

```yaml
# Prometheus configuration for modular services
prometheus:
  global:
    scrape_interval: 15s
    evaluation_interval: 15s
  
  scrape_configs:
    - job_name: 'rag-core'
      static_configs:
        - targets: ['rag-core:8000']
      metrics_path: '/metrics'
      scrape_interval: 30s
    
    - job_name: 'knowledge-mgmt'
      static_configs:
        - targets: ['knowledge-mgmt:8001']
      metrics_path: '/metrics'
      scrape_interval: 30s
    
    - job_name: 'ui-service'
      static_configs:
        - targets: ['ui-service:3000']
      metrics_path: '/metrics'
      scrape_interval: 30s
```

#### 3.2 Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Modular Services Overview",
    "panels": [
      {
        "title": "Service Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=~'rag-core|knowledge-mgmt|ui-service'}",
            "legendFormat": "{{job}}"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{job}} - {{method}} {{status}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ]
      }
    ]
  }
}
```

### 4. Message Bus Integration

#### 4.1 Redis Streams Configuration

```python
# Redis Streams integration for modular services
import redis
import json
from typing import Dict, Any

class EventBus:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.streams = {
            'document_events': 'documents:*',
            'query_events': 'queries:*',
            'knowledge_events': 'knowledge:*',
            'user_events': 'users:*'
        }
    
    async def publish_event(self, stream: str, event_type: str, data: Dict[str, Any]):
        event = {
            'event_type': event_type,
            'timestamp': time.time(),
            'data': json.dumps(data)
        }
        await self.redis_client.xadd(stream, event)
    
    async def subscribe_to_stream(self, stream: str, consumer_group: str, consumer_name: str):
        await self.redis_client.xgroup_create(stream, consumer_group, mkstream=True)
        while True:
            messages = await self.redis_client.xreadgroup(
                consumer_group, consumer_name,
                {stream: '>'},
                count=1,
                block=1000
            )
            for stream_name, messages in messages:
                for message_id, fields in messages:
                    yield {
                        'stream': stream_name,
                        'message_id': message_id,
                        'data': fields
                    }
                    await self.redis_client.xack(stream, consumer_group, message_id)

# Usage in services
event_bus = EventBus(redis.Redis(host='redis', port=6379))

# RAG Core service
async def process_query(query: str):
    # Process query
    result = await rag_service.process(query)
    
    # Publish event
    await event_bus.publish_event(
        'query_events',
        'query_processed',
        {'query': query, 'result': result}
    )
    
    return result

# Knowledge Management service
async def handle_document_event(event_data: Dict[str, Any]):
    if event_data['event_type'] == 'document_processed':
        # Update knowledge base
        await knowledge_service.update_knowledge(event_data['data'])
```

#### 4.2 Event-Driven Architecture

```yaml
# Event-driven architecture configuration
event_driven_architecture:
  streams:
    document_processing:
      producers: ['crawler', 'knowledge-mgmt']
      consumers: ['rag-core', 'ui-service']
      events: ['document_ingested', 'document_processed', 'document_indexed']
    
    query_processing:
      producers: ['ui-service', 'rag-core']
      consumers: ['knowledge-mgmt', 'ui-service']
      events: ['query_received', 'query_processed', 'response_generated']
    
    user_management:
      producers: ['ui-service']
      consumers: ['knowledge-mgmt', 'rag-core']
      events: ['user_created', 'user_updated', 'user_deleted']
```

### 5. Database Integration

#### 5.1 PostgreSQL Schema Management

```sql
-- Schema for modular services
CREATE SCHEMA rag_core;
CREATE SCHEMA knowledge_mgmt;
CREATE SCHEMA ui_service;

-- RAG Core schema
CREATE TABLE rag_core.queries (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    response_text TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    user_id INTEGER,
    session_id VARCHAR(255)
);

CREATE TABLE rag_core.sessions (
    id VARCHAR(255) PRIMARY KEY,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    last_activity TIMESTAMP DEFAULT NOW()
);

-- Knowledge Management schema
CREATE TABLE knowledge_mgmt.documents (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500),
    content TEXT,
    source_url VARCHAR(1000),
    created_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE knowledge_mgmt.chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES knowledge_mgmt.documents(id),
    content TEXT,
    embedding_vector VECTOR(1536),
    created_at TIMESTAMP DEFAULT NOW()
);

-- UI Service schema
CREATE TABLE ui_service.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);

CREATE TABLE ui_service.interactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES ui_service.users(id),
    interaction_type VARCHAR(100),
    interaction_data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 5.2 Database Connection Management

```python
# Database connection management for modular services
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator

class DatabaseManager:
    def __init__(self, database_url: str):
        self.engine = create_async_engine(
            database_url,
            pool_size=20,
            max_overflow=0,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        self.async_session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

# Service-specific database managers
rag_core_db = DatabaseManager(os.getenv('RAG_CORE_DATABASE_URL'))
knowledge_mgmt_db = DatabaseManager(os.getenv('KNOWLEDGE_MGMT_DATABASE_URL'))
ui_service_db = DatabaseManager(os.getenv('UI_SERVICE_DATABASE_URL'))
```

### 6. Caching Integration

#### 6.1 Redis Caching Strategy

```python
# Redis caching for modular services
import redis.asyncio as redis
import json
from typing import Any, Optional

class CacheManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        value = await self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600):
        await self.redis_client.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str):
        await self.redis_client.delete(key)
    
    async def invalidate_pattern(self, pattern: str):
        keys = await self.redis_client.keys(pattern)
        if keys:
            await self.redis_client.delete(*keys)

# Usage in services
cache = CacheManager(redis.Redis(host='redis', port=6379))

# RAG Core caching
async def get_query_response(query: str) -> str:
    cache_key = f"query:{hash(query)}"
    
    # Check cache first
    cached_response = await cache.get(cache_key)
    if cached_response:
        return cached_response
    
    # Process query
    response = await process_query(query)
    
    # Cache result
    await cache.set(cache_key, response, ttl=1800)  # 30 minutes
    
    return response

# Knowledge Management caching
async def get_document_chunks(document_id: int) -> List[Dict]:
    cache_key = f"document_chunks:{document_id}"
    
    cached_chunks = await cache.get(cache_key)
    if cached_chunks:
        return cached_chunks
    
    # Fetch from database
    chunks = await fetch_chunks_from_db(document_id)
    
    # Cache result
    await cache.set(cache_key, chunks, ttl=3600)  # 1 hour
    
    return chunks
```

#### 6.2 Multi-Level Caching

```yaml
# Multi-level caching configuration
caching:
  levels:
    l1:  # In-memory cache
      type: "python_lru_cache"
      size: 1000
      ttl: 300  # 5 minutes
    
    l2:  # Redis cache
      type: "redis"
      host: "redis"
      port: 6379
      ttl: 3600  # 1 hour
    
    l3:  # Database cache
      type: "postgres"
      table: "cache_entries"
      ttl: 86400  # 24 hours

# Cache invalidation strategy
cache_invalidation:
  strategies:
    - type: "time_based"
      ttl: 3600
    - type: "event_based"
      events: ["document_updated", "knowledge_refreshed"]
    - type: "manual"
      endpoints: ["/cache/invalidate"]
```

### 7. Security Integration

#### 7.1 Authentication and Authorization

```python
# JWT-based authentication using existing infrastructure
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import Dict, Any

class AuthService:
    def __init__(self, secret_key: str, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.security = HTTPBearer()
    
    def create_token(self, user_id: str, expires_delta: timedelta = None) -> str:
        expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
        payload = {
            'user_id': user_id,
            'exp': expire,
            'iat': datetime.utcnow(),
            'services': ['rag-core', 'knowledge-mgmt', 'ui-service']
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())) -> Dict[str, Any]:
        try:
            payload = jwt.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

# Service-specific authentication
auth_service = AuthService(os.getenv('JWT_SECRET'))

async def get_current_user(token: str = Depends(auth_service.verify_token)):
    return token['user_id']

# Usage in endpoints
@router.get("/protected")
async def protected_endpoint(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id, "message": "Protected endpoint accessed"}
```

#### 7.2 Rate Limiting

```python
# Redis-based rate limiting using existing Redis infrastructure
from redis.asyncio import Redis
import time
from typing import Optional

class RateLimiter:
    def __init__(self, redis_client: Redis, requests_per_minute: int = 60):
        self.redis_client = redis_client
        self.requests_per_minute = requests_per_minute
    
    async def is_allowed(self, identifier: str) -> bool:
        current_time = int(time.time())
        window_start = current_time - 60
        
        # Remove old entries
        await self.redis_client.zremrangebyscore(identifier, 0, window_start)
        
        # Count current requests
        current_requests = await self.redis_client.zcard(identifier)
        
        if current_requests >= self.requests_per_minute:
            return False
        
        # Add current request
        await self.redis_client.zadd(identifier, {str(current_time): current_time})
        await self.redis_client.expire(identifier, 60)
        
        return True

# Middleware integration
rate_limiter = RateLimiter(redis.Redis(host='redis', port=6379))

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host
    if not await rate_limiter.is_allowed(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    return await call_next(request)
```

### 8. Development Environment Integration

#### 8.1 Local Development Setup

```yaml
# docker-compose.override.yml for development
version: '3.8'

services:
  # Extend existing services for development
  consul:
    ports:
      - "8500:8500"
    environment:
      - CONSUL_DEV_MODE=true
      - CONSUL_LOG_LEVEL=DEBUG
  
  caddy:
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./caddy/config:/etc/caddy:ro
  
  grafana:
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - ./grafana/provisioning:/etc/grafana/provisioning
  
  # New modular services
  rag-core-dev:
    build:
      context: ./services/rag-core
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
    volumes:
      - ./services/rag-core:/app:ro
      - ./configs:/app/configs:ro
    depends_on:
      - consul
      - redis
      - postgres
  
  knowledge-mgmt-dev:
    build:
      context: ./services/knowledge-mgmt
      dockerfile: Dockerfile
      target: development
    ports:
      - "8001:8001"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
    volumes:
      - ./services/knowledge-mgmt:/app:ro
      - ./configs:/app/configs:ro
    depends_on:
      - consul
      - redis
      - postgres
  
  ui-service-dev:
    build:
      context: ./services/ui-service
      dockerfile: Dockerfile
      target: development
    ports:
      - "3000:3000"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
    volumes:
      - ./services/ui-service:/app:ro
      - ./configs:/app/configs:ro
    depends_on:
      - consul
      - redis
      - postgres
```

#### 8.2 Development Tools Integration

```yaml
# Development tools using existing infrastructure
services:
  # Extend existing development tools
  portainer:
    ports:
      - "9443:9443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
  
  # New development tools for modular services
  swagger-ui:
    image: swaggerapi/swagger-ui
    ports:
      - "8080:8080"
    environment:
      - SWAGGER_JSON=/foo/swagger.json
    volumes:
      - ./services/rag-core/docs:/foo:ro
  
  api-docs:
    image: stoplight/prism:4
    ports:
      - "4010:4010"
    command: mock -h 0.0.0.0 ./openapi.yaml
    volumes:
      - ./api-specs:/specs:ro
  
  # Integration with existing monitoring
  jaeger:
    image: jaegertracing/all-in-one:1.49
    ports:
      - "16686:16686"
      - "14268:14268"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
  
  # Integration with existing logging
  fluentd-dev:
    image: fluent/fluentd:v1.16-debian-1
    ports:
      - "24224:24224"
      - "24224:24224/udp"
    volumes:
      - ./fluentd/dev.conf:/fluentd/etc/fluent.conf:ro
      - ./logs:/var/log/containers:ro
```

### 9. Deployment Integration

#### 9.1 Production Deployment

```yaml
# Production deployment using existing infrastructure
version: '3.8'

services:
  # Use existing production services
  consul:
    image: consul:1.16.1
    command: consul agent -server -bootstrap-expect=3 -ui -client=0.0.0.0 -log-level=INFO
    volumes:
      - consul_data:/consul/data
      - ./consul/config:/consul/config:ro
    ports:
      - "8500:8500"
    restart: unless-stopped
    networks:
      - xnai_network
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
  
  # New modular services in production
  rag-core:
    image: xnai/rag-core:${VERSION:-latest}
    environment:
      - ENVIRONMENT=production
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
      - QDRANT_HOST=qdrant
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 30s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    networks:
      - xnai_network
    depends_on:
      - consul
      - redis
      - postgres
      - qdrant
  
  knowledge-mgmt:
    image: xnai/knowledge-mgmt:${VERSION:-latest}
    environment:
      - ENVIRONMENT=production
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 30s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    networks:
      - xnai_network
    depends_on:
      - consul
      - redis
      - postgres
  
  ui-service:
    image: xnai/ui-service:${VERSION:-latest}
    environment:
      - ENVIRONMENT=production
      - CONSUL_HOST=consul
      - REDIS_HOST=redis
      - POSTGRES_HOST=postgres
    deploy:
      replicas: 2
      update_config:
        parallelism: 1
        delay: 30s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.125'
    networks:
      - xnai_network
    depends_on:
      - consul
      - redis
      - postgres

volumes:
  consul_data:
    driver: local

networks:
  xnai_network:
    external: true
```

#### 9.2 Blue-Green Deployment

```yaml
# Blue-green deployment using existing infrastructure
version: '3.8'

services:
  # Blue environment
  rag-core-blue:
    image: xnai/rag-core:${BLUE_VERSION:-latest}
    environment:
      - ENVIRONMENT=production
      - DEPLOYMENT_ENVIRONMENT=blue
    deploy:
      replicas: 3
      labels:
        - "deployment=blue"
    networks:
      - xnai_network
  
  # Green environment
  rag-core-green:
    image: xnai/rag-core:${GREEN_VERSION:-latest}
    environment:
      - ENVIRONMENT=production
      - DEPLOYMENT_ENVIRONMENT=green
    deploy:
      replicas: 3
      labels:
        - "deployment=green"
    networks:
      - xnai_network
  
  # Load balancer configuration for blue-green
  caddy:
    image: caddy:2.8-alpine
    volumes:
      - ./caddy/blue-green.caddyfile:/etc/caddy/Caddyfile:ro
    ports:
      - "80:80"
      - "443:443"
    networks:
      - xnai_network
    depends_on:
      - rag-core-blue
      - rag-core-green

# Blue-green Caddy configuration
# caddy/blue-green.caddyfile
rag-core.xnai.example.com {
    # Route to blue environment by default
    reverse_proxy rag-core-blue:8000 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
        health_timeout 10s
        health_status 200
    }
    
    # Route to green environment when enabled
    @green {
        header_delegated X-Deployment green
    }
    reverse_proxy @green rag-core-green:8000 {
        lb_policy round_robin
        health_uri /health
        health_interval 30s
        health_timeout 10s
        health_status 200
    }
}
```

### 10. Monitoring and Observability Integration

#### 10.1 Metrics Integration

```python
# Prometheus metrics integration using existing VictoriaMetrics
from prometheus_client import Counter, Histogram, Gauge
import time
from typing import Dict, Any

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Number of active connections')
CACHE_HIT_RATE = Gauge('cache_hit_rate', 'Cache hit rate')

class MetricsCollector:
    @staticmethod
    def record_request(method: str, endpoint: str, status: str, duration: float):
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.observe(duration)
    
    @staticmethod
    def record_cache_hit(cache_type: str):
        CACHE_HIT_RATE.labels(cache_type=cache_type).inc()
    
    @staticmethod
    def record_active_connections(count: int):
        ACTIVE_CONNECTIONS.set(count)

# Middleware for automatic metrics collection
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    MetricsCollector.record_request(
        method=request.method,
        endpoint=request.url.path,
        status=str(response.status_code),
        duration=duration
    )
    
    return response
```

#### 10.2 Distributed Tracing

```python
# OpenTelemetry tracing using existing Jaeger infrastructure
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

def setup_tracing(service_name: str):
    # Configure tracer
    trace.set_tracer_provider(TracerProvider())
    tracer = trace.get_tracer(service_name)
    
    # Configure Jaeger exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="jaeger",
        agent_port=6831,
    )
    
    # Configure span processor
    span_processor = BatchSpanProcessor(jaeger_exporter)
    trace.get_tracer_provider().add_span_processor(span_processor)
    
    # Instrument frameworks
    FastAPIInstrumentor.instrument(app)
    RedisInstrumentor().instrument()
    SQLAlchemyInstrumentor().instrument()
    
    return tracer

# Setup tracing for each service
tracer = setup_tracing("rag-core")

# Use tracing in service functions
@tracer.start_as_current_span("process_query")
async def process_query(query: str):
    with tracer.start_as_current_span("validate_query") as span:
        span.set_attribute("query.length", len(query))
        if not query.strip():
            raise ValueError("Query cannot be empty")
    
    with tracer.start_as_current_span("search_vectors") as span:
        span.set_attribute("search.type", "vector")
        results = await vector_search(query)
        span.set_attribute("results.count", len(results))
    
    return results
```

## Implementation Roadmap

### Phase 1: Foundation Integration (Weeks 1-2)
- [ ] Integrate Consul service discovery for new services
- [ ] Configure Caddy load balancing for modular services
- [ ] Set up VictoriaMetrics monitoring for new services
- [ ] Configure Redis Streams for event-driven communication

### Phase 2: Database and Caching (Weeks 3-4)
- [ ] Set up PostgreSQL schemas for modular services
- [ ] Configure Redis caching for new services
- [ ] Implement database connection management
- [ ] Set up multi-level caching strategy

### Phase 3: Security and Authentication (Weeks 5-6)
- [ ] Integrate JWT authentication across services
- [ ] Configure rate limiting using existing Redis
- [ ] Set up service mesh security with Consul
- [ ] Implement secrets management

### Phase 4: Development and Deployment (Weeks 7-8)
- [ ] Set up development environment integration
- [ ] Configure production deployment using existing infrastructure
- [ ] Implement blue-green deployment strategy
- [ ] Set up comprehensive monitoring and observability

## Conclusion

This integration strategy leverages the existing sophisticated infrastructure to provide a solid foundation for the modular architecture. By building upon the current 24-service ecosystem, the strategy ensures:

- **Consistency**: Using existing patterns and configurations
- **Reliability**: Leveraging proven infrastructure components
- **Scalability**: Building on existing load balancing and monitoring
- **Security**: Using established authentication and authorization
- **Maintainability**: Following existing operational practices

The strategy provides a seamless transition from the current monolithic architecture to a modular service architecture while maximizing the value of existing infrastructure investments.