# XNAi Foundation: Portable Service Deployment Strategy

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Strategy for deploying modular services across different environments

## Overview

This portable deployment strategy enables the XNAi Foundation modular services to be deployed consistently across various environments (development, staging, production, edge locations) while maintaining the flexibility to run independently or as part of the larger ecosystem.

## Deployment Environment Analysis

### Current Deployment Infrastructure

#### Existing Docker Compose Setup
- **24 services** with sophisticated orchestration
- **Multi-environment support** (dev, staging, production)
- **Service mesh** with Consul and Caddy
- **Advanced monitoring** with VictoriaMetrics and Grafana
- **Load balancing** with health checks and SSL termination
- **Database clustering** with PostgreSQL
- **Vector database** with Qdrant
- **Message bus** with Redis Streams

#### Current Deployment Patterns
- **Development**: Local Docker Compose with hot reloading
- **Staging**: Docker Compose with production-like configuration
- **Production**: Docker Compose with resource limits and monitoring
- **Edge**: Not currently supported (opportunity for modular services)

### Target Deployment Environments

#### 1. Development Environment
- **Purpose**: Local development and testing
- **Requirements**: Fast iteration, hot reloading, debugging support
- **Constraints**: Limited resources, developer-friendly configuration

#### 2. Staging Environment
- **Purpose**: Integration testing and validation
- **Requirements**: Production-like configuration, automated testing
- **Constraints**: Resource efficiency, automated deployment

#### 3. Production Environment
- **Purpose**: Live service delivery
- **Requirements**: High availability, scalability, security
- **Constraints**: Resource optimization, monitoring, compliance

#### 4. Edge Environment
- **Purpose**: Local/offline deployment
- **Requirements**: Minimal dependencies, offline operation
- **Constraints**: Limited connectivity, resource constraints

## Portable Deployment Architecture

### 1. Environment-Agnostic Service Design

#### 1.1 Configuration Management

```yaml
# Environment-agnostic configuration structure
config/
  defaults.yaml              # Default configuration values
  development.yaml          # Development overrides
  staging.yaml              # Staging overrides
  production.yaml           # Production overrides
  edge.yaml                 # Edge deployment overrides
  
  services/
    rag-core/
      config.yaml           # Service-specific defaults
      development.yaml      # Development overrides
      production.yaml       # Production overrides
    knowledge-mgmt/
      config.yaml           # Service-specific defaults
      edge.yaml             # Edge-specific configuration
    ui-service/
      config.yaml           # Service-specific defaults
      production.yaml       # Production overrides
```

#### 1.2 Environment Detection and Configuration Loading

```python
# Environment-aware configuration loading
import os
import yaml
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.base_config = self._load_config('defaults')
        self.service_config = self._load_service_config()
        self.env_config = self._load_env_config()
    
    def _load_config(self, config_type: str) -> Dict[str, Any]:
        config_path = Path(__file__).parent / f'../config/{config_type}.yaml'
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_service_config(self) -> Dict[str, Any]:
        service_config_path = Path(__file__).parent / f'../config/services/{self.service_name}/config.yaml'
        if service_config_path.exists():
            with open(service_config_path, 'r') as f:
                return yaml.safe_load(f)
        return {}
    
    def _load_env_config(self) -> Dict[str, Any]:
        environment = os.getenv('ENVIRONMENT', 'development')
        env_config_path = Path(__file__).parent / f'../config/{environment}.yaml'
        service_env_config_path = Path(__file__).parent / f'../config/services/{self.service_name}/{environment}.yaml'
        
        env_config = {}
        if env_config_path.exists():
            with open(env_config_path, 'r') as f:
                env_config.update(yaml.safe_load(f))
        
        if service_env_config_path.exists():
            with open(service_env_config_path, 'r') as f:
                env_config.update(yaml.safe_load(f))
        
        return env_config
    
    def get_config(self) -> Dict[str, Any]:
        # Merge configurations with precedence: env > service > base
        config = {}
        config.update(self.base_config)
        config.update(self.service_config)
        config.update(self.env_config)
        
        # Override with environment variables
        for key, value in config.items():
            env_var = f"{self.service_name.upper()}_{key.upper()}"
            if env_var in os.environ:
                config[key] = os.environ[env_var]
        
        return config

# Usage in services
config_manager = ConfigManager('rag-core')
config = config_manager.get_config()
```

### 2. Multi-Environment Docker Compose

#### 2.1 Base Configuration

```yaml
# docker-compose.base.yml
version: '3.8'

services:
  # Shared infrastructure services
  consul:
    image: consul:1.16.1
    container_name: xnai_consul
    command: consul agent -server -bootstrap-expect=1 -ui -client=0.0.0.0 -log-level=INFO
    volumes:
      - consul_data:/consul/data
      - ./consul/config:/consul/config:ro
    ports:
      - "8500:8500"
    restart: unless-stopped
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8500/v1/status/leader"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7.0.12-alpine
    container_name: xnai_redis
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    restart: unless-stopped
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15.4
    container_name: xnai_postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    environment:
      - POSTGRES_DB=${POSTGRES_DB:-xnai}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    ports:
      - "5432:5432"
    restart: unless-stopped
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-postgres}"]
      interval: 30s
      timeout: 10s
      retries: 3

  qdrant:
    image: qdrant/qdrant:v1.5.0
    container_name: xnai_qdrant
    volumes:
      - qdrant_data:/qdrant/storage
    ports:
      - "6333:6333"
    environment:
      - QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
      - QDRANT__CLUSTER__ENABLED=true
      - QDRANT__SERVICE__GRPC_PORT=6334
    restart: unless-stopped
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/readyz"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  consul_data:
    driver: local
  redis_data:
    driver: local
  postgres_data:
    driver: local
  qdrant_data:
    driver: local

networks:
  xnai_network:
    driver: bridge
```

#### 2.2 Development Override

```yaml
# docker-compose.override.yml (Development)
version: '3.8'

services:
  # Development-specific overrides
  consul:
    environment:
      - CONSUL_DEV_MODE=true
      - CONSUL_LOG_LEVEL=DEBUG
    ports:
      - "8500:8500"

  # Modular services for development
  rag-core:
    build:
      context: ./services/rag-core
      dockerfile: Dockerfile
      target: development
    ports:
      - "8000:8000"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    volumes:
      - ./services/rag-core:/app:ro
      - ./config:/app/config:ro
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    networks:
      - xnai_network

  knowledge-mgmt:
    build:
      context: ./services/knowledge-mgmt
      dockerfile: Dockerfile
      target: development
    ports:
      - "8001:8001"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    volumes:
      - ./services/knowledge-mgmt:/app:ro
      - ./config:/app/config:ro
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
    networks:
      - xnai_network

  ui-service:
    build:
      context: ./services/ui-service
      dockerfile: Dockerfile
      target: development
    ports:
      - "3000:3000"
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    volumes:
      - ./services/ui-service:/app:ro
      - ./config:/app/config:ro
    command: ["npm", "run", "dev"]
    networks:
      - xnai_network
```

#### 2.3 Production Override

```yaml
# docker-compose.production.yml
version: '3.8'

services:
  # Production-specific overrides
  consul:
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
    environment:
      - CONSUL_LOG_LEVEL=INFO

  # Production modular services
  rag-core:
    image: xnai/rag-core:${VERSION:-latest}
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
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  knowledge-mgmt:
    image: xnai/knowledge-mgmt:${VERSION:-latest}
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
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  ui-service:
    image: xnai/ui-service:${VERSION:-latest}
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
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    networks:
      - xnai_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### 2.4 Edge Deployment Configuration

```yaml
# docker-compose.edge.yml
version: '3.8'

services:
  # Edge-optimized services with minimal dependencies
  rag-core-edge:
    build:
      context: ./services/rag-core
      dockerfile: Dockerfile.edge
      target: edge
    image: xnai/rag-core:edge
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=edge
      - LOG_LEVEL=INFO
      - OFFLINE_MODE=true
      - EMBEDDING_MODEL=local
    volumes:
      - ./models:/app/models:ro
      - ./data:/app/data
    networks:
      - xnai_edge_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  knowledge-mgmt-edge:
    build:
      context: ./services/knowledge-mgmt
      dockerfile: Dockerfile.edge
      target: edge
    image: xnai/knowledge-mgmt:edge
    ports:
      - "8001:8001"
    environment:
      - ENVIRONMENT=edge
      - LOG_LEVEL=INFO
      - OFFLINE_MODE=true
      - DOCUMENT_STORAGE=local
    volumes:
      - ./documents:/app/documents
      - ./processed:/app/processed
    networks:
      - xnai_edge_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Local-only dependencies for edge
  postgres-edge:
    image: postgres:15.4
    environment:
      - POSTGRES_DB=xnai_edge
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_edge_data:/var/lib/postgresql/data
      - ./postgres/init:/docker-entrypoint-initdb.d
    networks:
      - xnai_edge_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  qdrant-edge:
    image: qdrant/qdrant:v1.5.0
    volumes:
      - qdrant_edge_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__API_KEY=${QDRANT_API_KEY}
      - QDRANT__CLUSTER__ENABLED=false
    networks:
      - xnai_edge_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/readyz"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_edge_data:
    driver: local
  qdrant_edge_data:
    driver: local

networks:
  xnai_edge_network:
    driver: bridge
```

### 3. Kubernetes Deployment Strategy

#### 3.1 Base Kubernetes Manifests

```yaml
# k8s/base/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: xnai
  labels:
    name: xnai
    environment: base
```

```yaml
# k8s/base/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: xnai-config
  namespace: xnai
data:
  environment: "production"
  log_level: "INFO"
  debug: "false"
  
  # Database configuration
  postgres_host: "postgres"
  postgres_port: "5432"
  postgres_db: "xnai"
  
  # Redis configuration
  redis_host: "redis"
  redis_port: "6379"
  
  # Qdrant configuration
  qdrant_host: "qdrant"
  qdrant_port: "6333"
```

```yaml
# k8s/base/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: xnai-secrets
  namespace: xnai
type: Opaque
data:
  postgres_password: <base64-encoded-password>
  qdrant_api_key: <base64-encoded-api-key>
  jwt_secret: <base64-encoded-secret>
```

#### 3.2 Service-Specific Deployments

```yaml
# k8s/rag-core/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-core
  namespace: xnai
  labels:
    app: rag-core
    version: v1
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-core
      version: v1
  template:
    metadata:
      labels:
        app: rag-core
        version: v1
    spec:
      serviceAccountName: rag-core-sa
      containers:
      - name: rag-core
        image: xnai/rag-core:v1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          valueFrom:
            configMapKeyRef:
              name: xnai-config
              key: environment
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: xnai-config
              key: log_level
        - name: QDRANT_HOST
          valueFrom:
            configMapKeyRef:
              name: xnai-config
              key: qdrant_host
        - name: QDRANT_API_KEY
          valueFrom:
            secretKeyRef:
              name: xnai-secrets
              key: qdrant_api_key
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: rag-core-logs
          mountPath: /app/logs
        - name: rag-core-cache
          mountPath: /app/cache
      volumes:
      - name: rag-core-logs
        persistentVolumeClaim:
          claimName: rag-core-logs-pvc
      - name: rag-core-cache
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: rag-core-service
  namespace: xnai
spec:
  selector:
    app: rag-core
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: rag-core-ingress
  namespace: xnai
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - rag-core.xnai.example.com
    secretName: rag-core-tls
  rules:
  - host: rag-core.xnai.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: rag-core-service
            port:
              number: 80
```

#### 3.3 Environment-Specific Overlays

```yaml
# k8s/overlays/development/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- deployment-patch.yaml

configMapGenerator:
- name: xnai-config
  behavior: merge
  literals:
  - environment=development
  - log_level=DEBUG
  - debug=true

images:
- name: xnai/rag-core
  newTag: development
```

```yaml
# k8s/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- ../../base

patchesStrategicMerge:
- deployment-patch.yaml

configMapGenerator:
- name: xnai-config
  behavior: merge
  literals:
  - environment=production
  - log_level=INFO
  - debug=false

images:
- name: xnai/rag-core
  newTag: v1.0.0
```

### 4. Edge Deployment Strategy

#### 4.1 Edge-Optimized Container Images

```dockerfile
# Dockerfile.edge for edge deployment
FROM python:3.12-slim-bookworm AS base

# Install minimal dependencies for edge
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -g 1001 appgroup && \
    useradd -m -u 1001 -g 1001 -s /bin/bash appuser

FROM base AS dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

FROM dependencies AS edge
WORKDIR /app
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app

# Remove development dependencies
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Pre-download models for offline operation
RUN mkdir -p /app/models && \
    # Download embedding model for offline use
    curl -L -o /app/models/embedding_model.bin \
    "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2/resolve/main/pytorch_model.bin"

USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 4.2 Edge Deployment Scripts

```bash
#!/bin/bash
# scripts/deploy-edge.sh

set -e

EDGE_HOST=${EDGE_HOST:-localhost}
EDGE_PORT=${EDGE_PORT:-22}
EDGE_USER=${EDGE_USER:-root}
EDGE_PATH=${EDGE_PATH:-/opt/xnai}

echo "Deploying XNAi Foundation to edge location: $EDGE_HOST"

# Build edge images
echo "Building edge-optimized images..."
docker build -f services/rag-core/Dockerfile.edge -t xnai/rag-core:edge ./services/rag-core
docker build -f services/knowledge-mgmt/Dockerfile.edge -t xnai/knowledge-mgmt:edge ./services/knowledge-mgmt

# Save images for offline transfer
echo "Saving images for transfer..."
docker save xnai/rag-core:edge | gzip > rag-core-edge.tar.gz
docker save xnai/knowledge-mgmt:edge | gzip > knowledge-mgmt-edge.tar.gz

# Transfer to edge location
echo "Transferring images to edge location..."
scp rag-core-edge.tar.gz $EDGE_USER@$EDGE_HOST:$EDGE_PATH/
scp knowledge-mgmt-edge.tar.gz $EDGE_USER@$EDGE_HOST:$EDGE_PATH/
scp docker-compose.edge.yml $EDGE_USER@$EDGE_HOST:$EDGE_PATH/
scp -r config $EDGE_USER@$EDGE_HOST:$EDGE_PATH/

# Deploy on edge location
ssh $EDGE_USER@$EDGE_HOST << EOF
cd $EDGE_PATH

# Load images
echo "Loading Docker images..."
docker load < rag-core-edge.tar.gz
docker load < knowledge-mgmt-edge.tar.gz

# Start services
echo "Starting edge services..."
docker-compose -f docker-compose.edge.yml up -d

# Verify deployment
echo "Verifying deployment..."
docker-compose -f docker-compose.edge.yml ps

echo "Edge deployment completed successfully!"
EOF

# Cleanup
rm -f rag-core-edge.tar.gz knowledge-mgmt-edge.tar.gz

echo "Edge deployment script completed!"
```

#### 4.3 Edge Configuration Management

```yaml
# config/edge.yaml
# Edge-specific configuration
edge:
  offline_mode: true
  sync_interval: 3600  # 1 hour
  local_storage: true
  compression_enabled: true

services:
  rag-core:
    embedding_model: "local"
    cache_size: "256MB"
    max_concurrent_requests: 10
  
  knowledge-mgmt:
    document_storage: "local"
    processing_batch_size: 10
    validation_enabled: false
  
  ui-service:
    offline_mode: true
    cache_static_assets: true
    service_worker_enabled: true

networking:
  local_only: true
  port_range:
    start: 8000
    end: 9000
  ssl_enabled: false  # Self-signed certificates for edge

security:
  authentication_required: false
  encryption_at_rest: true
  data_retention_days: 30
```

### 5. Deployment Automation

#### 5.1 CI/CD Pipeline Configuration

```yaml
# .github/workflows/deploy.yml
name: Deploy Modular Services

on:
  push:
    branches: [main]
    tags: ['v*']
  workflow_dispatch:
    inputs:
      environment:
        description: 'Deployment environment'
        required: true
        default: 'staging'
        type: choice
        options:
        - development
        - staging
        - production
        - edge

env:
  REGISTRY: ghcr.io
  IMAGE_TAG: ${{ github.sha }}
  ENVIRONMENT: ${{ github.event.inputs.environment || 'staging' }}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [rag-core, knowledge-mgmt, ui-service]
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: ${{ env.REGISTRY }}/xnai/${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=raw,value=${{ env.IMAGE_TAG }}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./services/${{ matrix.service }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY }}/xnai/${{ matrix.service }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY }}/xnai/${{ matrix.service }}:buildcache,mode=max

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: ${{ env.ENVIRONMENT }}
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Deploy to ${{ env.ENVIRONMENT }}
        run: |
          case "${{ env.ENVIRONMENT }}" in
            "development")
              ./scripts/deploy-development.sh
              ;;
            "staging")
              ./scripts/deploy-staging.sh
              ;;
            "production")
              ./scripts/deploy-production.sh
              ;;
            "edge")
              ./scripts/deploy-edge.sh
              ;;
          esac
```

#### 5.2 Environment-Specific Deployment Scripts

```bash
#!/bin/bash
# scripts/deploy-production.sh

set -e

echo "Deploying to production environment..."

# Set production environment variables
export ENVIRONMENT=production
export VERSION=${GITHUB_SHA:0:7}

# Deploy infrastructure
echo "Deploying infrastructure..."
docker-compose -f docker-compose.base.yml -f docker-compose.production.yml up -d

# Wait for infrastructure to be ready
echo "Waiting for infrastructure to be ready..."
sleep 60

# Deploy services
echo "Deploying services..."
docker-compose -f docker-compose.base.yml -f docker-compose.production.yml up -d rag-core knowledge-mgmt ui-service

# Run health checks
echo "Running health checks..."
./scripts/health-check.sh production

# Run smoke tests
echo "Running smoke tests..."
./scripts/smoke-tests.sh production

echo "Production deployment completed successfully!"
```

```bash
#!/bin/bash
# scripts/deploy-edge.sh

set -e

EDGE_HOST=${1:-localhost}
EDGE_USER=${2:-root}
EDGE_PATH=${3:-/opt/xnai}

echo "Deploying to edge location: $EDGE_HOST"

# Build edge images
echo "Building edge-optimized images..."
docker build -f services/rag-core/Dockerfile.edge -t xnai/rag-core:edge ./services/rag-core
docker build -f services/knowledge-mgmt/Dockerfile.edge -t xnai/knowledge-mgmt:edge ./services/knowledge-mgmt

# Create deployment package
echo "Creating deployment package..."
tar -czf xnai-edge-deployment.tar.gz \
    docker-compose.edge.yml \
    config/ \
    services/rag-core/Dockerfile.edge \
    services/knowledge-mgmt/Dockerfile.edge

# Transfer to edge location
echo "Transferring to edge location..."
scp xnai-edge-deployment.tar.gz $EDGE_USER@$EDGE_HOST:$EDGE_PATH/
scp rag-core-edge.tar.gz $EDGE_USER@$EDGE_HOST:$EDGE_PATH/
scp knowledge-mgmt-edge.tar.gz $EDGE_USER@$EDGE_HOST:$EDGE_PATH/

# Deploy on edge location
ssh $EDGE_USER@$EDGE_HOST << EOF
cd $EDGE_PATH

# Extract deployment package
tar -xzf xnai-edge-deployment.tar.gz

# Load images
docker load < rag-core-edge.tar.gz
docker load < knowledge-mgmt-edge.tar.gz

# Start services
docker-compose -f docker-compose.edge.yml up -d

# Verify deployment
docker-compose -f docker-compose.edge.yml ps

echo "Edge deployment completed successfully!"
EOF

# Cleanup
rm -f xnai-edge-deployment.tar.gz rag-core-edge.tar.gz knowledge-mgmt-edge.tar.gz

echo "Edge deployment completed!"
```

### 6. Monitoring and Observability

#### 6.1 Environment-Specific Monitoring

```yaml
# monitoring/production-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: production-monitoring
  namespace: xnai
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "alert_rules.yml"
    
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
    
    alerting:
      alertmanagers:
        - static_configs:
            - targets:
              - alertmanager:9093

  alert_rules.yml: |
    groups:
    - name: service_health
      rules:
      - alert: ServiceDown
        expr: up{job=~"rag-core|knowledge-mgmt|ui-service"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service {{ \$labels.job }} is down"
          description: "{{ \$labels.job }} has been down for more than 1 minute"
      
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High error rate on {{ \$labels.job }}"
          description: "Error rate is {{ \$value }} errors per second"
      
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time on {{ \$labels.job }}"
          description: "95th percentile response time is {{ \$value }} seconds"
```

#### 6.2 Edge Monitoring

```yaml
# monitoring/edge-monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: edge-monitoring
  namespace: xnai
data:
  edge-monitoring.yml: |
    # Edge-specific monitoring configuration
    edge_monitoring:
      offline_mode: true
      local_metrics: true
      sync_interval: 3600  # Sync metrics every hour when online
      
      metrics:
        - name: "service_uptime"
          type: "gauge"
          description: "Service uptime in seconds"
        
        - name: "local_storage_usage"
          type: "gauge"
          description: "Local storage usage percentage"
        
        - name: "offline_requests"
          type: "counter"
          description: "Number of requests served in offline mode"
      
      alerts:
        - name: "StorageFull"
          condition: "local_storage_usage > 90"
          message: "Local storage is 90% full"
        
        - name: "ServiceUnhealthy"
          condition: "service_uptime < 300"
          message: "Service has been down for more than 5 minutes"
```

### 7. Rollback and Recovery

#### 7.1 Automated Rollback Strategy

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

ENVIRONMENT=${1:-production}
SERVICE=${2:-all}
PREVIOUS_VERSION=${3:-}

echo "Rolling back $SERVICE in $ENVIRONMENT environment..."

# Get previous version if not specified
if [ -z "$PREVIOUS_VERSION" ]; then
    PREVIOUS_VERSION=$(docker images --format "table {{.Repository}}:{{.Tag}}" | \
        grep "xnai/$SERVICE" | \
        head -2 | \
        tail -1 | \
        cut -d: -f2)
fi

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Error: Could not determine previous version"
    exit 1
fi

echo "Rolling back to version: $PREVIOUS_VERSION"

case "$ENVIRONMENT" in
    "development")
        docker-compose -f docker-compose.override.yml stop $SERVICE
        docker-compose -f docker-compose.override.yml pull $SERVICE
        docker-compose -f docker-compose.override.yml up -d $SERVICE
        ;;
    "staging")
        docker-compose -f docker-compose.base.yml -f docker-compose.staging.yml stop $SERVICE
        docker-compose -f docker-compose.base.yml -f docker-compose.staging.yml pull $SERVICE
        docker-compose -f docker-compose.base.yml -f docker-compose.staging.yml up -d $SERVICE
        ;;
    "production")
        # Blue-green deployment rollback
        docker-compose -f docker-compose.base.yml -f docker-compose.production.yml stop $SERVICE
        docker tag xnai/$SERVICE:$PREVIOUS_VERSION xnai/$SERVICE:latest
        docker-compose -f docker-compose.base.yml -f docker-compose.production.yml up -d $SERVICE
        ;;
    "edge")
        # Edge rollback with local images
        ssh $EDGE_USER@$EDGE_HOST << EOF
        cd $EDGE_PATH
        docker-compose -f docker-compose.edge.yml stop $SERVICE
        docker-compose -f docker-compose.edge.yml pull $SERVICE
        docker-compose -f docker-compose.edge.yml up -d $SERVICE
        EOF
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

# Verify rollback
echo "Verifying rollback..."
sleep 30
./scripts/health-check.sh $ENVIRONMENT

echo "Rollback completed successfully!"
```

#### 7.2 Disaster Recovery

```bash
#!/bin/bash
# scripts/disaster-recovery.sh

set -e

ENVIRONMENT=${1:-production}
BACKUP_DATE=${2:-$(date +%Y-%m-%d)}

echo "Starting disaster recovery for $ENVIRONMENT environment..."

# Restore from backup
case "$ENVIRONMENT" in
    "production")
        echo "Restoring production environment from backup..."
        
        # Stop all services
        docker-compose -f docker-compose.base.yml -f docker-compose.production.yml down
        
        # Restore databases
        echo "Restoring databases..."
        docker run --rm \
            -v postgres_backup:/backup \
            -v xnai_postgres_data:/var/lib/postgresql/data \
            postgres:15.4 \
            pg_restore -U postgres -d xnai /backup/postgres_backup.sql
        
        # Restore vector database
        echo "Restoring vector database..."
        docker run --rm \
            -v qdrant_backup:/backup \
            -v xnai_qdrant_data:/qdrant/storage \
            alpine tar xzf /backup/qdrant_data.tar.gz -C /
        
        # Restart services
        docker-compose -f docker-compose.base.yml -f docker-compose.production.yml up -d
        
        # Verify recovery
        ./scripts/health-check.sh production
        ;;
    
    "edge")
        echo "Restoring edge environment from backup..."
        
        ssh $EDGE_USER@$EDGE_HOST << EOF
        cd $EDGE_PATH
        
        # Stop services
        docker-compose -f docker-compose.edge.yml down
        
        # Restore local data
        if [ -f backup/edge_backup.tar.gz ]; then
            tar -xzf backup/edge_backup.tar.gz -C /
        fi
        
        # Restart services
        docker-compose -f docker-compose.edge.yml up -d
        
        # Verify recovery
        docker-compose -f docker-compose.edge.yml ps
        EOF
        ;;
    
    *)
        echo "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

echo "Disaster recovery completed successfully!"
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Implement environment-agnostic configuration management
- [ ] Create multi-environment Docker Compose configurations
- [ ] Set up base Kubernetes manifests
- [ ] Configure edge-optimized container images

### Phase 2: Deployment Automation (Weeks 3-4)
- [ ] Implement CI/CD pipeline for modular services
- [ ] Create environment-specific deployment scripts
- [ ] Set up automated testing and validation
- [ ] Configure rollback and recovery procedures

### Phase 3: Edge Deployment (Weeks 5-6)
- [ ] Implement edge deployment strategy
- [ ] Create edge-optimized configurations
- [ ] Set up edge monitoring and observability
- [ ] Test offline operation capabilities

### Phase 4: Production Readiness (Weeks 7-8)
- [ ] Implement production deployment procedures
- [ ] Set up comprehensive monitoring
- [ ] Configure disaster recovery
- [ ] Validate deployment across all environments

## Conclusion

This portable deployment strategy provides a comprehensive approach to deploying XNAi Foundation modular services across various environments. By leveraging the existing sophisticated infrastructure and implementing environment-specific optimizations, the strategy ensures:

- **Consistency**: Uniform deployment process across all environments
- **Flexibility**: Support for development, staging, production, and edge deployments
- **Reliability**: Automated rollback and disaster recovery procedures
- **Scalability**: Kubernetes support for production environments
- **Accessibility**: Edge deployment for offline and resource-constrained scenarios

The strategy builds upon the existing 24-service ecosystem while providing the foundation for flexible, portable deployment of modular services across diverse environments.