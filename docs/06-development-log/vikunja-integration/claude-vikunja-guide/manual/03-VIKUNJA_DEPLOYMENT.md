# Vikunja Implementation Manual - Part 3: Docker Compose & Deployment

**Version**: 1.0  
**Updated**: 2026-02-07  
**Estimated Time**: 2 hours  
**Target Audience**: Cline (Local Developer Assistant)

---

## Table of Contents

1. [Updated docker-compose.yml (Foundation Core)](#updated-docker-composeyml-foundation-core)
2. [Caddyfile (Unified Reverse Proxy)](#caddyfile-unified-reverse-proxy)
3. [Create docker-compose.vikunja.yml (Overlay)](#create-docker-composevikunjayml-overlay)
4. [Updated Makefile](#updated-makefile)
5. [Deployment Steps](#deployment-steps)

---

## Updated docker-compose.yml (Foundation Core)

### Instructions for Cline

**IMPORTANT**: This replaces the monolithic Vikunja service in your current docker-compose.yml with a unified Caddy proxy.

```bash
# Cline: Step 1 - Backup current compose
cp docker-compose.yml docker-compose.yml.backup.vikunja

# Step 2 - Remove the old Vikunja service section
# Find and delete the vikunja service block (lines: vikunja: through command: [...])
# vim docker-compose.yml  # OR use your editor

# Step 3 - Add Caddy service (see below)
# Insert the Caddy service definition after the 'mkdocs' service
```

### Complete Updated docker-compose.yml

```yaml
# ============================================================================
# Xoe-NovAi Foundation Stack - Phase 1 v0.1.7 (Multi-Service Optimized)
# ============================================================================
# Purpose: Multi-service orchestration for the Xoe-NovAi Foundation Stack.
# Changes: 
#   - Removed monolithic Vikunja service
#   - Added Caddy unified reverse proxy (port 80)
#   - All services now behind Caddy (zero exposed ports except :80)
# Optimization: AMD Ryzen 5700U (Zen 2) | 8 Cores / 16 Threads
# Security: Zero-Trust, Rootless Podman, Ma'at Ethical Guardrails
# ============================================================================

version: '3.8'

services:
  # ==========================================================================
  # REDIS SERVICE - Cache & Streams Coordinator
  # ==========================================================================
  redis:
    image: redis:7.4.1-alpine
    container_name: xnai_redis
    init: true
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    command: redis-server --requirepass "${REDIS_PASSWORD:?REDIS_PASSWORD must be set}" --maxmemory 512mb --maxmemory-policy allkeys-lru
    volumes:
      - ./data/redis:/data:Z,U
    environment:
      - REDIS_PASSWORD
      - REDIS_STREAM_MAX_LEN=${REDIS_STREAM_MAX_LEN:-1000}
    healthcheck:
      test: ["CMD", "sh", "-c", "redis-cli -a \"$REDIS_PASSWORD\" ping || exit 1"]
      interval: 30s
      timeout: 15s
      retries: 5
      start_period: 30s
    networks:
      - xnai_network
    restart: unless-stopped

  # ==========================================================================
  # RAG SERVICE - FastAPI Backend (Ryzen Tuned)
  # ==========================================================================
  rag:
    build:
      context: .
      dockerfile: Dockerfile
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: xnai-rag:latest
    container_name: xnai_rag_api
    init: true
    cpuset: "0,2,4,6,8,10,12,14"
    mem_limit: 4g
    memswap_limit: 4g
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2.0'
        reservations:
          memory: 2G
          cpus: '1.0'
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
      - CHOWN
      - SETUID
      - SETGID
    read_only: true
    tmpfs:
      - /tmp:size=512m,mode=1777
      - /var/run:size=64m,mode=0755
      - /app/.cache:size=100m,mode=0755
      - /app/logs:size=100m,mode=1777
      - /app/data:size=50m,mode=1777
    volumes:
      - ./config.toml:/app/config.toml:ro
      - ./models:/models:ro
      - ./embeddings:/embeddings:ro
      - ./library:/library:Z,U
      - ./knowledge:/knowledge:Z,U
      - ./data/faiss_index:/app/data/faiss_index:Z,U
      - ./backups:/backups:Z,U
      - ./data/prometheus-multiproc:/prometheus_data:Z,U
      - ./app/XNAi_rag_app:/app/XNAi_rag_app:ro
    environment:
      - OPENBLAS_CORETYPE=ZEN
      - OPENBLAS_NUM_THREADS=6
      - LLAMA_CPP_N_THREADS=6
      - LLAMA_CPP_USE_MLOCK=true
      - LLAMA_CPP_USE_MMAP=true
      - OMP_NUM_THREADS=1
      - LLM_MODEL_PATH=/models/Qwen3-0.6B-Q6_K.gguf
      - RAG_API_URL=http://rag:8000
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - REDIS_PASSWORD_FILE=/run/secrets/redis_password
      - IAM_DB_PATH=/app/data/iam.db
      - JWT_PRIVATE_KEY_PATH=/app/data/jwt-private-key.pem
      - JWT_PUBLIC_KEY_PATH=/app/data/jwt-public-key.pem
      - LOG_DIR=/app/logs
      - API_KEY_FILE=/run/secrets/api_key
      - DEBUG_MODE=true
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app
    secrets:
      - redis_password
      - api_key
    networks:
      - xnai_network
    depends_on:
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 15s
      retries: 5
      start_period: 30s
    restart: unless-stopped
    command:
      - sh
      - -c
      - |
        echo '🚀 Starting XNAi Foundation RAG API...'
        [ -f /run/secrets/redis_password ] || (echo '❌ Missing Redis Secret' && exit 1)
        uvicorn XNAi_rag_app.api.entrypoint:app --host 0.0.0.0 --port 8000 --log-level info

  # ==========================================================================
  # UI SERVICE - Chainlit Frontend (Voice Enabled)
  # ==========================================================================
  ui:
    build:
      context: .
      dockerfile: Dockerfile.chainlit
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: xnai-ui:latest
    container_name: xnai_chainlit_ui
    init: true
    cpuset: "1,3,5,7,9,11,13,15"
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
    tmpfs:
      - /app/logs:size=100m,mode=1777
    volumes:
      - ./config.toml:/app/config.toml:ro
      - ./models:/models:ro
      - ./app/XNAi_rag_app:/app/XNAi_rag_app
      - ./assets:/app/assets
    environment:
      - OPENBLAS_CORETYPE=ZEN
      - OPENBLAS_NUM_THREADS=6
      - CHAINLIT_PORT=8001
      - CHAINLIT_NO_TELEMETRY=true
      - RAG_API_URL=http://rag:8000
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - LOG_DIR=/app/logs
      - PYTHONUNBUFFERED=1
      - PYTHONPATH=/app
    depends_on:
      redis:
        condition: service_healthy
      rag:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/"]
      interval: 30s
      timeout: 15s
      retries: 5
      start_period: 90s
    networks:
      - xnai_network
    restart: unless-stopped
    command:
      - sh
      - -c
      - |
        echo '🚀 Starting XNAi Foundation UI...'
        chainlit run XNAi_rag_app/ui/chainlit_app_voice.py --host 0.0.0.0 --port 8001

  # ==========================================================================
  # CRAWLER SERVICE - Ingestion Engine
  # ==========================================================================
  crawler:
    build:
      context: .
      dockerfile: Dockerfile.crawl
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: xnai-crawler:latest
    container_name: xnai_crawler
    init: true
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    volumes:
      - ./config.toml:/app/config.toml:ro
      - ./library:/library:Z,U
      - ./knowledge:/knowledge:Z,U
      - ./data/cache:/app/cache:Z,U
      - ./app/XNAi_rag_app:/app/XNAi_rag_app
      - /tmp/crawl4ai:/app/.crawl4ai
      - /tmp/crawler_logs:/app/logs
    environment:
      - OPENBLAS_CORETYPE=ZEN
      - N_THREADS=6
      - CRAWL4AI_NO_TELEMETRY=true
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - LIBRARY_PATH=/library
      - KNOWLEDGE_PATH=/knowledge
      - LOG_DIR=/app/logs
    depends_on:
      redis:
        condition: service_healthy
      rag:
        condition: service_healthy
    networks:
      - xnai_network
    restart: unless-stopped
    command: ["sh", "-c", "echo '🚀 Crawler service standby...' && while true; do sleep 3600; done"]

  # ==========================================================================
  # CURATION WORKER - Knowledge Refinement
  # ==========================================================================
  curation_worker:
    build:
      context: .
      dockerfile: Dockerfile.curation_worker
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: xnai-curation-worker:latest
    container_name: xnai_curation_worker
    init: true
    restart: on-failure
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    depends_on:
      - redis
    environment:
      - OPENBLAS_CORETYPE=ZEN
      - OPENBLAS_NUM_THREADS=6
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - REDIS_PASSWORD=${REDIS_PASSWORD}
      - DATA_DIR=/app/data/curations
      - LOG_DIR=/app/logs/curations
      - PYTHONPATH=/app
    volumes:
      - ./data/curations:/app/data/curations:Z,U
      - ./logs/curations:/app/logs/curations:Z,U
      - ./app/XNAi_rag_app:/app/XNAi_rag_app:ro
    networks:
      - xnai_network

  # ==========================================================================
  # MKDOCS SERVICE - Foundation Documentation
  # ==========================================================================
  mkdocs:
    build:
      context: .
      dockerfile: Dockerfile.docs
      args:
        BUILDKIT_INLINE_CACHE: 1
    image: xnai-mkdocs:latest
    container_name: xnai_mkdocs
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    volumes:
      - ./mkdocs.yml:/workspace/mkdocs.yml:ro
      - ./docs:/workspace/docs:ro
      - ./docs-new:/workspace/docs-new:ro
    environment:
      - OPENBLAS_CORETYPE=ZEN
      - N_THREADS=2
    networks:
      - xnai_network
    restart: unless-stopped
    command:
      - sh
      - -c
      - |
        echo '🚀 Starting XNAi Foundation Docs...'
        cd /workspace && mkdocs serve --config-file mkdocs.yml --dev-addr=0.0.0.0:8000

  # ==========================================================================
  # CADDY SERVICE - Unified Reverse Proxy & TLS Termination
  # ========== REPLACES DIRECT PORT EXPOSURE ==========
  # ==========================================================================
  caddy:
    image: caddy:2.7.6-alpine
    container_name: xnai_caddy
    init: true
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE
    read_only: true
    tmpfs:
      - /tmp:size=100m,mode=1777
      - /etc/caddy/data:size=50m,mode=0755
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - ./certs:/etc/caddy/certs:Z,U,ro
    environment:
      - CADDY_ADMIN=127.0.0.1:2019
    networks:
      - xnai_network
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      redis:
        condition: service_healthy
      rag:
        condition: service_healthy
      ui:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://127.0.0.1:2019/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    restart: unless-stopped

# ============================================================================
# NETWORKS & VOLUMES
# ============================================================================
networks:
  xnai_network:
    driver: bridge
    name: xnai_network

secrets:
  redis_password:
    external: true  # Created via: podman secret create redis_password < ...
  api_key:
    external: true
```

**Changes from Previous Version**:
- ✅ Removed monolithic Vikunja service (now in separate overlay)
- ✅ Added Caddy reverse proxy (listens on port 80/443)
- ✅ All internal ports no longer exposed directly (hidden behind Caddy)
- ✅ Secrets marked as `external: true` (created via `podman secret create`)

---

## Caddyfile (Unified Reverse Proxy)

### Create the Caddyfile

```bash
# Cline: Create Caddy reverse proxy configuration
cat > Caddyfile << 'EOF'
# ============================================================================
# Caddy Configuration - Xoe-NovAi Unified Reverse Proxy
# ============================================================================
# Version: 1.0 (Foundation + Vikunja support)
# Updated: 2026-02-07
# Purpose: Single entrypoint for all services (port 80 → internal services)
# ============================================================================

# Global options
{
  # Disable telemetry (Ma'at 42 compliance)
  admin 127.0.0.1:2019
  
  # Structured logging
  log {
    output file /tmp/caddy_access.log
    format json
  }
}

# HTTP listener - unified reverse proxy
:80 {
  # Security headers (global)
  header {
    Strict-Transport-Security "max-age=31536000; includeSubDomains"
    X-Content-Type-Options "nosniff"
    X-Frame-Options "SAMEORIGIN"
    X-XSS-Protection "1; mode=block"
    Referrer-Policy "strict-origin-when-cross-origin"
    Permissions-Policy "camera=(), microphone=(), geolocation=()"
  }

  # ========== FOUNDATION SERVICES ==========
  
  # RAG API (FastAPI backend)
  /api/v1* {
    reverse_proxy rag:8000 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      header_up X-Real-IP {remote_host}
      
      # Health check configuration
      health_uri /health
      health_interval 30s
      health_timeout 5s
      health_status 200
    }
  }

  # Chainlit UI (WebSocket + static assets)
  / {
    reverse_proxy ui:8001 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      websocket
    }
  }

  # Metrics (admin only - no external access)
  /metrics {
    respond "Forbidden" 403
  }

  # ========== VIKUNJA SERVICES (Overlay) ==========
  
  # Vikunja API
  /vikunja/api/* {
    reverse_proxy vikunja-api:3456 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      header_up X-Real-IP {remote_host}
      
      # Health check
      health_uri /api/v1/info
      health_interval 30s
      health_timeout 5s
    }
  }

  # Vikunja Frontend (SPA with WebSocket for real-time updates)
  /vikunja/* {
    reverse_proxy vikunja-api:3456 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      websocket
    }
  }

  # ========== FALLBACK ==========
  
  handle {
    respond "Service not found (check Caddy config)" 404
  }
}

# ============================================================================
# Health Monitoring & Admin API
# ============================================================================
# Caddy admin API: http://127.0.0.1:2019 (localhost only)
# Reload config (no downtime): caddy reload -c Caddyfile
# View active config: curl http://127.0.0.1:2019/config/
EOF

echo "✅ Created: Caddyfile"
```

**Key Features**:
- ✅ WebSocket support for Chainlit (real-time voice/chat)
- ✅ Health checks per upstream (Caddy auto-disables if unhealthy)
- ✅ X-Forwarded-* headers preserve request metadata
- ✅ `/metrics` explicitly blocked (admin-only)
- ✅ Vikunja path routing: `/vikunja/*` → vikunja-api:3456

---

## Create docker-compose.vikunja.yml (Overlay)

### Instructions for Cline

```bash
# Cline: This is a NEW file (doesn't replace anything)
cat > docker-compose.vikunja.yml << 'EOF'
# ============================================================================
# Xoe-NovAi Vikunja Multi-Service Overlay
# ============================================================================
# Purpose: Isolated task management & project coordination (optional)
# Usage: podman compose -f docker-compose.yml -f docker-compose.vikunja.yml up
# Toggle: Omit `-f docker-compose.vikunja.yml` to disable
# Data Persistence: PostgreSQL bind mount at ./data/vikunja/
# Created: 2026-02-07
# ============================================================================

version: '3.8'

services:
  # ==========================================================================
  # VIKUNJA DATABASE - PostgreSQL 16 (Ryzen Optimized)
  # ==========================================================================
  vikunja-db:
    image: postgres:16-alpine
    container_name: xnai_vikunja_db
    init: true
    user: "${APP_UID:-1001}:${APP_GID:-1001}"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
    read_only: true
    tmpfs:
      - /var/run/postgresql:size=50m,mode=0700
      - /tmp:size=100m,mode=1777
    volumes:
      - ./data/vikunja/db:/var/lib/postgresql/data:Z,U
      - ./config/postgres.conf:/etc/postgresql.conf:ro
    environment:
      POSTGRES_USER: vikunja
      POSTGRES_PASSWORD_FILE: /run/secrets/vikunja_db_password
      POSTGRES_DB: vikunja
      POSTGRES_INITDB_ARGS: "-c config_file=/etc/postgresql.conf"
      PGUSER: vikunja
    secrets:
      - vikunja_db_password
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U vikunja -h 127.0.0.1"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s
    networks:
      - xnai_network
    restart: unless-stopped

  # ==========================================================================
  # VIKUNJA API - Backend Service (Go Binary + Frontend Assets)
  # ==========================================================================
  vikunja-api:
    image: vikunja/vikunja:0.24.1
    container_name: xnai_vikunja_api
    init: true
    user: "1000:1000"
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    read_only: true
    tmpfs:
      - /tmp:size=100m,mode=1777
      - /vikunja/temp:size=50m,mode=0755
    volumes:
      - ./data/vikunja/files:/app/vikunja/files:Z,U
    environment:
      # Database Configuration
      VIKUNJA_DATABASE_TYPE: postgres
      VIKUNJA_DATABASE_HOST: vikunja-db
      VIKUNJA_DATABASE_PORT: "5432"
      VIKUNJA_DATABASE_USER: vikunja
      VIKUNJA_DATABASE_PASSWORD_FILE: /run/secrets/vikunja_db_password
      VIKUNJA_DATABASE_DATABASE: vikunja
      VIKUNJA_DATABASE_MAXOPENCONNECTIONS: "20"
      VIKUNJA_DATABASE_MAXIDLECONNECTIONS: "5"

      # Service Configuration
      VIKUNJA_SERVICE_PUBLICURL: "http://localhost/vikunja"
      VIKUNJA_SERVICE_JWTEXPIRATION: "86400"
      VIKUNJA_SERVICE_JWTEXPIRATIONLOGIN: "1209600"
      VIKUNJA_SERVICE_STATICDIR: "/app/vikunja/public"
      
      # JWT Secret (injected from Podman secret)
      VIKUNJA_SERVICE_JWTSECRET_FILE: /run/secrets/vikunja_jwt_secret
      
      # CORS (disabled, Caddy handles reverse proxy)
      VIKUNJA_CORS_ENABLE: "false"

      # Features
      VIKUNJA_ENABLECALENDAR: "true"
      VIKUNJA_ENABLESYNC: "false"

      # File Storage
      VIKUNJA_FILES_MAXSIZE: "20971520"

      # Authentication
      VIKUNJA_AUTH_LOCAL_ENABLED: "true"
      VIKUNJA_AUTH_OPENID_ENABLED: "false"

      # Redis (optional session/cache backend)
      VIKUNJA_REDIS_ENABLED: "true"
      VIKUNJA_REDIS_HOST: redis
      VIKUNJA_REDIS_PORT: "6379"
      VIKUNJA_REDIS_PASSWORD_FILE: /run/secrets/redis_password
      VIKUNJA_REDIS_DB: "5"

      # Logging
      VIKUNJA_LOGGER_LEVEL: "info"

      # Mailer (disabled for air-gapped)
      VIKUNJA_MAILER_ENABLED: "false"

    secrets:
      - vikunja_db_password
      - vikunja_jwt_secret
      - redis_password

    healthcheck:
      test: ["CMD-SHELL", "wget --quiet --tries=1 --spider http://127.0.0.1:3456/api/v1/info || exit 1"]
      interval: 20s
      timeout: 10s
      retries: 5
      start_period: 45s

    depends_on:
      vikunja-db:
        condition: service_healthy
      redis:
        condition: service_healthy

    networks:
      - xnai_network

    restart: unless-stopped

# ============================================================================
# NETWORK & SECRETS (External References)
# ============================================================================
networks:
  xnai_network:
    external: true  # Reuse Foundation network (defined in docker-compose.yml)

secrets:
  vikunja_db_password:
    external: true  # Created via: podman secret create vikunja_db_password < ...
  vikunja_jwt_secret:
    external: true
  redis_password:
    external: true  # Shared with Foundation (created in Part 2)
EOF

echo "✅ Created: docker-compose.vikunja.yml"
```

**Key Configuration Notes**:

| Setting | Value | Reason |
|---------|-------|--------|
| **Image** | `vikunja/vikunja:0.24.1` | Bundled binary (API + Frontend) |
| **User** | `1000:1000` | Standard container user |
| **Volume flags** | `:Z,U` | Rootless Podman security |
| **Redis DB** | `5` | Foundation uses 0-4 |
| **Max connections** | `20` | <6GB system limit |
| **CORS** | `false` | Caddy handles proxy |
| **Mailer** | `false` | Air-gapped (no external email) |

---

## Updated Makefile

### Add Vikunja Targets to Makefile

```bash
# Cline: Append these targets to your existing Makefile

cat >> Makefile << 'EOF'

# ============================================================================
# VIKUNJA OVERLAY TARGETS
# ============================================================================
# Usage: make [target]
# Examples:
#   make up-vikunja           # Start Foundation + Vikunja
#   make down-vikunja         # Stop Vikunja (keep Foundation)
#   make restart-vikunja      # Cycle Vikunja services
#   make logs-vikunja         # Tail Vikunja logs
# ============================================================================

.PHONY: up-vikunja down-vikunja restart-vikunja logs-vikunja

up-vikunja: up
	@echo "🚀 Starting Vikunja overlay..."
	@mkdir -p data/vikunja/{db,files}
	@podman unshare chown 1000:1000 -R data/vikunja 2>/dev/null || true
	@podman compose -f docker-compose.yml -f docker-compose.vikunja.yml up -d
	@sleep 10
	@echo "⏳ Waiting for services to stabilize..."
	@sleep 10
	@$(MAKE) health

down-vikunja:
	@echo "🛑 Stopping Vikunja overlay..."
	@podman compose -f docker-compose.yml -f docker-compose.vikunja.yml down

restart-vikunja: down-vikunja up-vikunja

logs-vikunja:
	@podman compose -f docker-compose.yml -f docker-compose.vikunja.yml logs -f vikunja-api vikunja-db

# Health check targets
health-vikunja:
	@echo "🏥 Vikunja health check..."
	@podman compose -f docker-compose.yml -f docker-compose.vikunja.yml ps
	@echo ""
	@echo "Testing Vikunja API..."
	@curl -s http://localhost/vikunja/api/v1/info | jq . || echo "❌ Vikunja API unreachable"
	@echo ""
	@echo "Testing PostgreSQL..."
	@podman compose -f docker-compose.yml -f docker-compose.vikunja.yml exec -T vikunja-db \
		pg_isready -U vikunja || echo "❌ PostgreSQL unhealthy"

EOF

echo "✅ Appended Vikunja targets to Makefile"
```

---

## Deployment Steps

### Step 1: Validate All Files Are in Place

```bash
# Cline: Verify all configuration files exist
ls -la \
  docker-compose.yml \
  docker-compose.vikunja.yml \
  Caddyfile \
  config/postgres.conf \
  config/vikunja-config.yaml \
  secrets/redis_password.txt \
  secrets/vikunja_db_password.txt \
  secrets/vikunja_jwt_secret.txt

# Expected: All files listed with appropriate permissions
```

### Step 2: Validate Docker Compose Syntax

```bash
# Cline: Check for YAML errors
echo "Validating Foundation compose..."
podman compose -f docker-compose.yml config > /dev/null && \
  echo "✅ docker-compose.yml valid" || echo "❌ docker-compose.yml has errors"

echo "Validating Vikunja overlay..."
podman compose -f docker-compose.vikunja.yml config > /dev/null && \
  echo "✅ docker-compose.vikunja.yml valid" || echo "❌ docker-compose.vikunja.yml has errors"

echo "Validating combined (Foundation + Vikunja)..."
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml config > /dev/null && \
  echo "✅ Combined compose valid" || echo "❌ Combined compose has errors"
```

### Step 3: Validate Caddyfile

```bash
# Cline: Caddy syntax check (requires Caddy or Docker)
podman run --rm -v $(pwd)/Caddyfile:/etc/caddy/Caddyfile:ro caddy:2.7.6-alpine \
  caddy validate --config /etc/caddy/Caddyfile && \
  echo "✅ Caddyfile valid" || echo "❌ Caddyfile has errors"
```

### Step 4: Create Podman Secrets

```bash
# Cline: Import secrets if not already created
podman secret create redis_password < secrets/redis_password.txt 2>/dev/null || \
  echo "ℹ️  redis_password already exists"

podman secret create vikunja_db_password < secrets/vikunja_db_password.txt 2>/dev/null || \
  echo "ℹ️  vikunja_db_password already exists"

podman secret create vikunja_jwt_secret < secrets/vikunja_jwt_secret.txt 2>/dev/null || \
  echo "ℹ️  vikunja_jwt_secret already exists"

echo ""
echo "Verify secrets created:"
podman secret list
```

### Step 5: Start Foundation Only (Smoke Test)

```bash
# Cline: Test Foundation stack first (without Vikunja)
echo "Starting Foundation services..."
podman compose -f docker-compose.yml down  # Clean slate
podman compose -f docker-compose.yml up -d

echo "⏳ Waiting 30s for services to stabilize..."
sleep 30

echo ""
echo "Checking Foundation health..."
podman compose -f docker-compose.yml ps
```

### Step 6: Verify Foundation Services

```bash
# Cline: Health checks for Foundation
echo "Testing RAG API..."
curl -s http://localhost/api/v1/health | jq . && echo "✅ RAG API healthy" || echo "❌ RAG API unhealthy"

echo ""
echo "Testing Chainlit UI..."
curl -s http://localhost/ | grep -q "chainlit" && echo "✅ Chainlit healthy" || echo "❌ Chainlit unhealthy"

echo ""
echo "Testing Redis..."
podman compose -f docker-compose.yml exec -T redis redis-cli -a $(cat secrets/redis_password.txt) ping | grep -q PONG && \
  echo "✅ Redis healthy" || echo "❌ Redis unhealthy"

echo ""
echo "Testing Caddy proxy..."
curl -I http://localhost/ | head -1 && echo "✅ Caddy responding" || echo "❌ Caddy not responding"
```

### Step 7: Start Vikunja Overlay

```bash
# Cline: Add Vikunja to running stack
echo "🚀 Starting Vikunja overlay..."

# Ensure data directory ownership
podman unshare chown 1000:1000 -R data/vikunja/ 2>/dev/null || true

# Start Vikunja (adds to existing Foundation)
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml up -d

echo "⏳ Waiting 45s for Vikunja to initialize..."
sleep 45

echo ""
echo "Checking Vikunja status..."
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml ps
```

### Step 8: Verify Vikunja Services

```bash
# Cline: Health checks for Vikunja
echo "Testing Vikunja API..."
curl -s http://localhost/vikunja/api/v1/info | jq . && echo "✅ Vikunja API healthy" || echo "❌ Vikunja API unhealthy"

echo ""
echo "Testing Vikunja Frontend..."
curl -s http://localhost/vikunja/ | grep -q "vikunja\|Vue\|html" && \
  echo "✅ Vikunja Frontend healthy" || echo "❌ Vikunja Frontend unhealthy"

echo ""
echo "Testing PostgreSQL..."
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml exec -T vikunja-db \
  pg_isready -U vikunja -h 127.0.0.1 && echo "✅ PostgreSQL healthy" || echo "❌ PostgreSQL unhealthy"

echo ""
echo "Testing Vikunja API via Caddy proxy..."
curl -s http://localhost/vikunja/api/v1/info | jq . && \
  echo "✅ Caddy → Vikunja proxy working" || echo "❌ Proxy issue"
```

### Step 9: Full Stack Health Check

```bash
# Cline: Comprehensive validation
cat > test-full-stack.sh << 'SCRIPT'
#!/bin/bash

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  Xoe-NovAi Full Stack Health Check                         ║"
echo "║  (Foundation + Vikunja)                                    ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Foundation Services
echo ""
echo "📊 Foundation Services Status:"
podman compose -f docker-compose.yml ps --format "table {{.Names}}\t{{.Status}}"

# Vikunja Services
echo ""
echo "📊 Vikunja Services Status:"
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml ps --format "table {{.Names}}\t{{.Status}}" | \
  grep vikunja || echo "⚠️  Vikunja services not running"

# Health Endpoints
echo ""
echo "🔗 API Endpoints:"
echo -n "   RAG API:         "; curl -s http://localhost/api/v1/health | jq -r '.status' 2>/dev/null || echo "❌ unreachable"
echo -n "   Chainlit:        "; curl -s http://localhost/ | grep -q "script" && echo "✅ running" || echo "❌ unreachable"
echo -n "   Vikunja API:     "; curl -s http://localhost/vikunja/api/v1/info | jq -r '.version' 2>/dev/null || echo "❌ unreachable"
echo -n "   Vikunja UI:      "; curl -I http://localhost/vikunja/ 2>/dev/null | grep -q "200\|301" && echo "✅ running" || echo "❌ unreachable"

# Memory Usage
echo ""
echo "💾 Memory Usage:"
podman stats --no-stream --format "table {{.Names}}\t{{.MemUsage}}" 2>/dev/null | head -15

# Logs (last 10 lines each)
echo ""
echo "📝 Recent Logs:"
echo ""
echo "RAG API (last 5 lines):"
podman compose -f docker-compose.yml logs rag --tail=5 | tail -5
echo ""
echo "Vikunja API (last 5 lines):"
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml logs vikunja-api --tail=5 | tail -5

echo ""
echo "✅ Health check complete!"
SCRIPT

chmod +x test-full-stack.sh
./test-full-stack.sh
```

### Step 10: Commit Configuration Changes

```bash
# Cline: Save all changes to git
git add \
  docker-compose.yml \
  docker-compose.vikunja.yml \
  Caddyfile \
  config/postgres.conf \
  config/vikunja-config.yaml \
  .env \
  Makefile \
  .gitignore

git commit -m "feat: Vikunja multi-file Compose integration (Phase 1)

- Add unified Caddy reverse proxy (port 80 entrypoint)
- Create isolated docker-compose.vikunja.yml overlay
- Implement PostgreSQL 16 Ryzen optimization
- Add Podman native secrets management
- Update Makefile with Vikunja targets
- Compliance: Ma'at 18 (modularity), 35 (security), 41 (leanness)

Closes: Vikunja Phase 1 Implementation"

echo "✅ Changes committed to git"
```

---

## Troubleshooting Deployment Issues

### Issue: "Permission denied" on data/vikunja/files

```bash
# Solution: Re-apply permissions
podman unshare chown 1000:1000 -R data/vikunja/
podman unshare chmod 700 data/vikunja/db
```

### Issue: PostgreSQL fails to start ("postmaster already running")

```bash
# Solution: Clean up stale Postgres process lock
rm -f data/vikunja/db/postmaster.pid
podman compose -f docker-compose.vikunja.yml restart vikunja-db
```

### Issue: Vikunja API can't connect to PostgreSQL ("connection refused")

```bash
# Verify PostgreSQL is healthy
podman compose -f docker-compose.vikunja.yml exec vikunja-db pg_isready -U vikunja

# Check logs
podman compose -f docker-compose.vikunja.yml logs vikunja-db
podman compose -f docker-compose.vikunja.yml logs vikunja-api
```

### Issue: Caddy proxy returns "502 Bad Gateway"

```bash
# Check upstream service health
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml ps | grep -E "vikunja|rag|ui"

# Test direct connection (bypass Caddy)
curl http://localhost:3456/api/v1/info  # Direct to Vikunja
curl http://localhost:8000/health       # Direct to RAG
```

---

**Next Step**: Proceed to Part 4 (Testing & Validation)

---

## Quick Reference: Common Commands

```bash
# Full stack (Foundation + Vikunja)
make up-vikunja             # Start everything
make down-vikunja           # Stop Vikunja overlay
make restart-vikunja        # Restart Vikunja
make logs-vikunja           # Tail Vikunja logs
make health-vikunja         # Health check

# Inspect running containers
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml ps
podman compose -f docker-compose.yml -f docker-compose.vikunja.yml logs vikunja-api --tail=50

# Access Vikunja database
podman compose -f docker-compose.vikunja.yml exec vikunja-db psql -U vikunja -d vikunja

# Reload Caddy config (no downtime)
podman exec xnai_caddy caddy reload -c /etc/caddy/Caddyfile
```

---

**Status: Ready for deployment** ✅
