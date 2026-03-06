# XNAi Foundation: Containerization Strategy

**Version**: 1.0.0  
**Date**: 2026-02-27  
**Status**: Design Phase  
**Purpose**: Comprehensive containerization strategy for modular services

## Overview

This containerization strategy builds upon the existing sophisticated Docker infrastructure to provide optimized, secure, and scalable container deployments for the modular architecture. It leverages the current 24-service ecosystem while implementing modern container best practices.

## Current Container Infrastructure Analysis

### Existing Docker Setup
- **24 services** with complex interdependencies
- **Multi-stage builds** with optimization
- **Service mesh** with Consul and Caddy
- **Advanced networking** with custom networks
- **Volume management** with data persistence
- **Security hardening** with non-root users
- **Resource management** with limits and reservations

### Current Docker Compose Features
- **Service discovery** via Consul
- **Load balancing** via Caddy with health checks
- **Monitoring** via VictoriaMetrics and Grafana
- **Message bus** via Redis Streams
- **Database clustering** with PostgreSQL
- **Vector database** with Qdrant
- **Documentation** with MkDocs
- **Project management** with Vikunja

## Containerization Strategy for Modular Services

### 1. Service-Specific Container Strategy

#### 1.1 Multi-Stage Build Optimization

```dockerfile
# Optimized multi-stage build for RAG Core service
FROM python:3.12-slim-bookworm AS base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -s /bin/bash -u 1001 appuser

FROM base AS dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev --no-interaction --no-ansi

FROM dependencies AS development
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DEBUG=true
ENV LOG_LEVEL=DEBUG
COPY . /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM dependencies AS production
WORKDIR /app
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
RUN python -m compileall /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### 1.2 Service-Specific Docker Compose

```yaml
# services/rag-core/docker-compose.yml
version: '3.8'

services:
  rag-core:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
      args:
        - ENVIRONMENT=production
        - BUILD_VERSION=${BUILD_VERSION:-latest}
    image: xnai/rag-core:${BUILD_VERSION:-latest}
    container_name: xnai_rag_core
    restart: unless-stopped
    
    # Environment configuration
    environment:
      - ENVIRONMENT=${ENVIRONMENT:-production}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - DEBUG=${DEBUG:-false}
      
      # Dependencies
      - QDRANT_HOST=${QDRANT_HOST:-qdrant}
      - QDRANT_PORT=${QDRANT_PORT:-6333}
      - QDRANT_API_KEY=${QDRANT_API_KEY}
      
      - REDIS_HOST=${REDIS_HOST:-redis}
      - REDIS_PORT=${REDIS_PORT:-6379}
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      
      - POSTGRES_HOST=${POSTGRES_HOST:-postgres}
      - POSTGRES_PORT=${POSTGRES_PORT:-5432}
      - POSTGRES_DB=${POSTGRES_DB:-xnai}
      - POSTGRES_USER=${POSTGRES_USER:-postgres}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    
    # Resource management
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    
    # Health checks
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    
    # Networking
    networks:
      - xnai_network
      - xnai_monitoring
    
    # Volumes
    volumes:
      - rag_core_logs:/app/logs
      - rag_core_cache:/app/cache
    
    # Dependencies
    depends_on:
      qdrant:
        condition: service_healthy
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy

volumes:
  rag_core_logs:
    driver: local
  rag_core_cache:
    driver: local

networks:
  xnai_network:
    external: true
  xnai_monitoring:
    external: true
```

### 2. Container Security Hardening

#### 2.1 Security-First Container Configuration

```dockerfile
# Security-hardened container base
FROM python:3.12-slim-bookworm AS secure-base

# Security updates
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    dumb-init \
    && rm -rf /var/lib/apt/lists/*

# Create dedicated user with specific UID/GID
RUN groupadd -g 1001 appgroup && \
    useradd -m -u 1001 -g 1001 -s /bin/bash appuser

# Set secure permissions
RUN chmod 755 /app && chown appuser:appgroup /app

# Security configurations
USER appuser
WORKDIR /app

# Security labels
LABEL security.non-root=true
LABEL security.seccomp=runtime/default
LABEL security.apparmor=runtime/default
```

#### 2.2 Container Security Scanning

```yaml
# .github/workflows/security-scan.yml
name: Container Security Scan

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t xnai/rag-core:security-test ./services/rag-core
      
      - name: Run Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'xnai/rag-core:security-test'
          format: 'sarif'
          output: 'trivy-results.sarif'
      
      - name: Upload Trivy scan results to GitHub Security tab
        uses: github/codeql-action/upload-sarif@v2
        if: always()
        with:
          sarif_file: 'trivy-results.sarif'
      
      - name: Run Snyk container scan
        uses: snyk/actions/docker@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          image: xnai/rag-core:security-test
          args: --severity-threshold=high
```

### 3. Container Orchestration

#### 3.1 Kubernetes Deployment Strategy

```yaml
# k8s/rag-core-deployment.yaml
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
  template:
    metadata:
      labels:
        app: rag-core
        version: v1
    spec:
      serviceAccountName: rag-core-sa
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
        runAsGroup: 1001
        fsGroup: 1001
      containers:
      - name: rag-core
        image: xnai/rag-core:v1.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: QDRANT_HOST
          valueFrom:
            configMapKeyRef:
              name: rag-core-config
              key: qdrant.host
        - name: QDRANT_API_KEY
          valueFrom:
            secretKeyRef:
              name: rag-core-secrets
              key: qdrant.api-key
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

#### 3.2 Docker Swarm Deployment

```yaml
# docker-stack.yml
version: '3.8'

services:
  rag-core:
    image: xnai/rag-core:${VERSION:-latest}
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
        order: start-first
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
      placement:
        constraints:
          - node.role == worker
    environment:
      - ENVIRONMENT=production
      - LOG_LEVEL=INFO
    networks:
      - xnai_network
    configs:
      - source: rag-core-config
        target: /app/config/config.yaml
    secrets:
      - rag-core-secrets
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

configs:
  rag-core-config:
    file: ./configs/rag-core.yaml

secrets:
  rag-core-secrets:
    external: true

networks:
  xnai_network:
    external: true
```

### 4. Container Registry Strategy

#### 4.1 Multi-Registry Setup

```yaml
# .github/workflows/container-build.yml
name: Build and Push Containers

on:
  push:
    branches: [main, dev]
    tags: ['v*']

env:
  REGISTRY_GITHUB: ghcr.io
  REGISTRY_DOCKER_HUB: docker.io
  REGISTRY_PRIVATE: registry.xnai.example.com

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    
    strategy:
      matrix:
        service: [rag-core, knowledge-mgmt, ui-service]
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v3
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2
      
      - name: Log in to GitHub Container Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY_GITHUB }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Log in to Docker Hub
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY_DOCKER_HUB }}
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Log in to Private Registry
        uses: docker/login-action@v2
        with:
          registry: ${{ env.REGISTRY_PRIVATE }}
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_PASSWORD }}
      
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v4
        with:
          images: |
            ${{ env.REGISTRY_GITHUB }}/xnai/${{ matrix.service }}
            ${{ env.REGISTRY_DOCKER_HUB }}/xnai/${{ matrix.service }}
            ${{ env.REGISTRY_PRIVATE }}/xnai/${{ matrix.service }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
      
      - name: Build and push
        uses: docker/build-push-action@v4
        with:
          context: ./services/${{ matrix.service }}
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=registry,ref=${{ env.REGISTRY_GITHUB }}/xnai/${{ matrix.service }}:buildcache
          cache-to: type=registry,ref=${{ env.REGISTRY_GITHUB }}/xnai/${{ matrix.service }}:buildcache,mode=max
```

#### 4.2 Container Image Optimization

```dockerfile
# Optimized container with multi-stage builds and caching
FROM python:3.12-slim-bookworm AS base

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    gcc \
    g++ \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -g 1001 appgroup \
    && useradd -m -u 1001 -g 1001 -s /bin/bash appuser

# Create cache mount for pip
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false

FROM base AS dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN --mount=type=cache,target=/root/.cache/pip \
    poetry install --no-dev --no-interaction --no-ansi

FROM dependencies AS runtime
WORKDIR /app
COPY --from=dependencies /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY . /app
RUN python -m compileall /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 5. Container Monitoring and Observability

#### 5.1 Container Metrics Collection

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  cadvisor:
    image: gcr.io/cadvisor/cadvisor:v0.47.0
    container_name: xnai_cadvisor
    privileged: true
    devices:
      - /dev/kmsg
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    ports:
      - "8080:8080"
    restart: unless-stopped
    networks:
      - xnai_monitoring
    depends_on:
      - prometheus

  node-exporter:
    image: prom/node-exporter:v1.6.1
    container_name: xnai_node_exporter
    user: root
    privileged: true
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
      - /etc/hostname:/etc/nodename:ro
      - /etc/hosts:/etc/nodehosts:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    ports:
      - "9100:9100"
    restart: unless-stopped
    networks:
      - xnai_monitoring
```

#### 5.2 Container Logging Strategy

```yaml
# docker-compose.logging.yml
version: '3.8'

services:
  fluentd:
    image: fluent/fluentd:v1.16-debian-1
    container_name: xnai_fluentd
    volumes:
      - ./fluentd/conf:/fluentd/etc
      - ./logs:/var/log/containers
    ports:
      - "24224:24224"
      - "24224:24224/udp"
    restart: unless-stopped
    networks:
      - xnai_logging
    depends_on:
      - elasticsearch

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.8.0
    container_name: xnai_elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"
    restart: unless-stopped
    networks:
      - xnai_logging

  kibana:
    image: docker.elastic.co/kibana/kibana:8.8.0
    container_name: xnai_kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    restart: unless-stopped
    networks:
      - xnai_logging
    depends_on:
      - elasticsearch

volumes:
  elasticsearch_data:

networks:
  xnai_logging:
    driver: bridge
```

### 6. Container Networking Strategy

#### 6.1 Service Mesh with Consul

```yaml
# docker-compose.service-mesh.yml
version: '3.8'

services:
  consul:
    image: consul:1.16.1
    container_name: xnai_consul
    command: consul agent -server -bootstrap-expect=1 -ui -client=0.0.0.0 -log-level=INFO
    volumes:
      - consul_data:/consul/data
      - ./consul/config:/consul/config
    ports:
      - "8500:8500"
      - "8600:8600/udp"
    restart: unless-stopped
    networks:
      - xnai_service_mesh
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8500/v1/status/leader"]
      interval: 30s
      timeout: 10s
      retries: 3

  consul-template:
    image: hashicorp/consul-template:0.30.1
    container_name: xnai_consul_template
    volumes:
      - ./consul/templates:/templates
      - ./caddy/config:/config
    command: consul-template -template "/templates/Caddyfile.ctmpl:/config/Caddyfile:docker-compose -f docker-compose.yml up -d caddy"
    depends_on:
      - consul
    networks:
      - xnai_service_mesh

volumes:
  consul_data:

networks:
  xnai_service_mesh:
    driver: bridge
```

#### 6.2 Load Balancing with Caddy

```caddyfile
# Caddyfile for service load balancing
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

### 7. Container Storage Strategy

#### 7.1 Persistent Storage Management

```yaml
# docker-compose.storage.yml
version: '3.8'

services:
  minio:
    image: minio/minio:RELEASE.2023-07-13T19-35-13Z
    container_name: xnai_minio
    volumes:
      - minio_data:/data
    ports:
      - "9000:9000"
      - "9001:9001"
    environment:
      - MINIO_ROOT_USER=${MINIO_ROOT_USER:-minioadmin}
      - MINIO_ROOT_PASSWORD=${MINIO_ROOT_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    restart: unless-stopped
    networks:
      - xnai_storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
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
      - xnai_storage
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
      - xnai_storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/readyz"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  minio_data:
    driver: local
  postgres_data:
    driver: local
  qdrant_data:
    driver: local

networks:
  xnai_storage:
    driver: bridge
```

#### 7.2 Backup and Recovery Strategy

```bash
#!/bin/bash
# scripts/backup-containers.sh

set -e

BACKUP_DIR="/backups/$(date +%Y-%m-%d)"
LOG_FILE="/var/log/backup.log"

echo "Starting container backup at $(date)" | tee -a $LOG_FILE

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
echo "Backing up PostgreSQL..." | tee -a $LOG_FILE
docker exec xnai_postgres pg_dump -U postgres xnai > $BACKUP_DIR/postgres_backup.sql

# Backup MinIO data
echo "Backing up MinIO data..." | tee -a $LOG_FILE
docker run --rm -v minio_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/minio_data.tar.gz /data

# Backup Qdrant data
echo "Backing up Qdrant data..." | tee -a $LOG_FILE
docker run --rm -v qdrant_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/qdrant_data.tar.gz /data

# Backup container configurations
echo "Backing up container configurations..." | tee -a $LOG_FILE
docker-compose config > $BACKUP_DIR/docker-compose.yml

# Compress backup
echo "Compressing backup..." | tee -a $LOG_FILE
tar -czf $BACKUP_DIR.tar.gz -C /backups $(basename $BACKUP_DIR)

# Upload to remote storage (optional)
if [ -n "$REMOTE_BACKUP_URL" ]; then
    echo "Uploading to remote storage..." | tee -a $LOG_FILE
    curl -X PUT -T $BACKUP_DIR.tar.gz "$REMOTE_BACKUP_URL/$(basename $BACKUP_DIR.tar.gz)"
fi

# Cleanup old backups (keep last 7 days)
echo "Cleaning up old backups..." | tee -a $LOG_FILE
find /backups -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed successfully at $(date)" | tee -a $LOG_FILE
```

### 8. Container Development Workflow

#### 8.1 Local Development Environment

```yaml
# docker-compose.override.yml (Development)
version: '3.8'

services:
  rag-core:
    build:
      context: ./services/rag-core
      dockerfile: Dockerfile
      target: development
    volumes:
      - ./services/rag-core:/app:ro
      - ./configs:/app/configs:ro
      - rag_core_logs:/app/logs
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    ports:
      - "8000:8000"
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
    networks:
      - xnai_network

  knowledge-mgmt:
    build:
      context: ./services/knowledge-mgmt
      dockerfile: Dockerfile
      target: development
    volumes:
      - ./services/knowledge-mgmt:/app:ro
      - ./configs:/app/configs:ro
      - knowledge_mgmt_logs:/app/logs
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    ports:
      - "8001:8001"
    command: ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
    networks:
      - xnai_network

  ui-service:
    build:
      context: ./services/ui-service
      dockerfile: Dockerfile
      target: development
    volumes:
      - ./services/ui-service:/app:ro
      - ./configs:/app/configs:ro
      - ui_service_logs:/app/logs
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
      - ENVIRONMENT=development
    ports:
      - "3000:3000"
    command: ["npm", "run", "dev"]
    networks:
      - xnai_network

volumes:
  rag_core_logs:
    driver: local
  knowledge_mgmt_logs:
    driver: local
  ui_service_logs:
    driver: local
```

#### 8.2 Development Tools Integration

```yaml
# docker-compose.dev-tools.yml
version: '3.8'

services:
  portainer:
    image: portainer/portainer-ce:2.21.0
    container_name: xnai_portainer
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - portainer_data:/data
    ports:
      - "9443:9443"
    restart: unless-stopped
    networks:
      - xnai_dev_tools

  dbeaver:
    image: dbeaver/cloudbeaver:23.0.2
    container_name: xnai_dbeaver
    volumes:
      - dbeaver_data:/opt/cloudbeaver/workspace
    ports:
      - "8978:8978"
    restart: unless-stopped
    networks:
      - xnai_dev_tools

  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: xnai_redis_commander
    environment:
      - REDIS_HOSTS=local:redis:6379
    ports:
      - "8081:8081"
    restart: unless-stopped
    networks:
      - xnai_dev_tools

  qdrant-console:
    image: qdrant/qdrant-console:v0.3.0
    container_name: xnai_qdrant_console
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    ports:
      - "6335:80"
    restart: unless-stopped
    networks:
      - xnai_dev_tools

volumes:
  portainer_data:
    driver: local
  dbeaver_data:
    driver: local

networks:
  xnai_dev_tools:
    driver: bridge
```

### 9. Container Performance Optimization

#### 9.1 Resource Optimization

```yaml
# docker-compose.performance.yml
version: '3.8'

services:
  rag-core:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    environment:
      - GUNICORN_WORKERS=4
      - GUNICORN_WORKER_CONNECTIONS=1000
      - GUNICORN_MAX_REQUESTS=1000
      - GUNICORN_MAX_REQUESTS_JITTER=100
      - UVICORN_WORKERS=2
      - UVICORN_TIMEOUT_KEEP_ALIVE=5

  knowledge-mgmt:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  ui-service:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.25'
        reservations:
          memory: 128M
          cpus: '0.125'
```

#### 9.2 Caching Strategy

```yaml
# docker-compose.caching.yml
version: '3.8'

services:
  redis-cache:
    image: redis:7.0.12-alpine
    container_name: xnai_redis_cache
    volumes:
      - redis_cache_data:/data
    ports:
      - "6380:6379"
    command: redis-server --appendonly yes --maxmemory 512mb --maxmemory-policy allkeys-lru
    restart: unless-stopped
    networks:
      - xnai_cache
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  memcached:
    image: memcached:1.6.22-alpine
    container_name: xnai_memcached
    ports:
      - "11211:11211"
    command: memcached -m 256 -c 1024 -v
    restart: unless-stopped
    networks:
      - xnai_cache

volumes:
  redis_cache_data:
    driver: local

networks:
  xnai_cache:
    driver: bridge
```

### 10. Container Security Best Practices

#### 10.1 Security Hardening

```yaml
# docker-compose.security.yml
version: '3.8'

services:
  rag-core:
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    read_only: true
    tmpfs:
      - /tmp:noexec,nosuid,size=100m
      - /app/logs:noexec,nosuid,size=100m
    user: "1001:1001"
    networks:
      - xnai_secure

  security-scanner:
    image: aquasec/trivy:latest
    container_name: xnai_security_scanner
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - trivy_cache:/root/.cache
    command: trivy image --exit-code 1 --severity HIGH,CRITICAL xnai/rag-core:latest
    networks:
      - xnai_secure

volumes:
  trivy_cache:
    driver: local

networks:
  xnai_secure:
    driver: bridge
    internal: true
```

#### 10.2 Secrets Management

```yaml
# docker-compose.secrets.yml
version: '3.8'

services:
  rag-core:
    secrets:
      - qdrant_api_key
      - redis_password
      - postgres_password
      - jwt_secret

secrets:
  qdrant_api_key:
    external: true
    name: qdrant_api_key
  redis_password:
    external: true
    name: redis_password
  postgres_password:
    external: true
    name: postgres_password
  jwt_secret:
    external: true
    name: jwt_secret
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-2)
- [ ] Implement multi-stage builds for all services
- [ ] Set up container security scanning
- [ ] Configure container monitoring
- [ ] Implement container logging strategy

### Phase 2: Orchestration (Weeks 3-4)
- [ ] Set up Kubernetes deployment configurations
- [ ] Configure Docker Swarm for production
- [ ] Implement service mesh with Consul
- [ ] Set up load balancing with Caddy

### Phase 3: Storage and Networking (Weeks 5-6)
- [ ] Configure persistent storage solutions
- [ ] Implement backup and recovery procedures
- [ ] Set up container networking
- [ ] Configure container caching

### Phase 4: Security and Optimization (Weeks 7-8)
- [ ] Implement container security hardening
- [ ] Configure secrets management
- [ ] Optimize container performance
- [ ] Set up container development workflow

## Conclusion

This containerization strategy provides a comprehensive approach to deploying and managing the modular XNAi Foundation services. By leveraging the existing sophisticated infrastructure and implementing modern container best practices, the strategy ensures:

- **Security**: Hardened containers with vulnerability scanning
- **Performance**: Optimized resource usage and caching
- **Reliability**: Health checks, monitoring, and backup procedures
- **Scalability**: Kubernetes and Docker Swarm support
- **Maintainability**: Clear development and deployment workflows

The strategy builds upon the existing 24-service ecosystem while providing the foundation for future growth and evolution of the modular architecture.