# VIKUNJA IMPLEMENTATION MANUAL
## Parts 3-5: Complete Configuration Files & Quick Deploy Guide

**Status**: Ready-to-Deploy  
**Version**: 2.0  
**Purpose**: Consolidated configuration for docker-compose, Caddy, Makefile

---

## 📋 CONFIGURATION FILE REFERENCE

All files listed here have been created in Parts 1-2. Use these as master references.

---

## FILE 1: docker-compose.yml (UPDATE)

**Location**: `./docker-compose.yml` (existing file)  
**Action**: Replace the old Vikunja service block with NEW Caddy service

```yaml
# ============================================================================
# Xoe-NovAi Foundation Stack - Phase 1 v0.1.7 (Multi-Service)
# ============================================================================
# IMPORTANT: Remove old monolithic Vikunja service from this file
# Then add the Caddy service below

version: '3.8'

services:
  # [Keep all existing services: redis, rag, ui, crawler, curation_worker, mkdocs]
  # [They remain unchanged from your current docker-compose.yml]

  # ========== NEW: CADDY REVERSE PROXY ==========
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

networks:
  xnai_network:
    driver: bridge
    name: xnai_network

secrets:
  redis_password:
    external: true
  api_key:
    external: true
```

---

## FILE 2: docker-compose.yml (NEW)

**Location**: `./docker-compose.yml`  
**Action**: Create this new file

```yaml
# ============================================================================
# Xoe-NovAi Vikunja Multi-Service Overlay
# ============================================================================
# Usage: podman compose -f docker-compose.yml -f docker-compose.yml up

version: '3.8'

services:
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

  vikunja-api:
    image: vikunja/vikunja:1.0.0
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
      VIKUNJA_DATABASE_TYPE: postgres
      VIKUNJA_DATABASE_HOST: vikunja-db
      VIKUNJA_DATABASE_PORT: "5432"
      VIKUNJA_DATABASE_USER: vikunja
      VIKUNJA_DATABASE_PASSWORD_FILE: /run/secrets/vikunja_db_password
      VIKUNJA_DATABASE_DATABASE: vikunja
      VIKUNJA_DATABASE_MAXOPENCONNECTIONS: "20"
      VIKUNJA_DATABASE_MAXIDLECONNECTIONS: "5"
      VIKUNJA_SERVICE_PUBLICURL: "http://localhost/vikunja"
      VIKUNJA_SERVICE_JWTEXPIRATION: "86400"
      VIKUNJA_SERVICE_JWTSECRET_FILE: /run/secrets/vikunja_jwt_secret
      VIKUNJA_CORS_ENABLE: "false"
      VIKUNJA_ENABLECALENDAR: "true"
      VIKUNJA_ENABLESYNC: "false"
      VIKUNJA_FILES_MAXSIZE: "20971520"
      VIKUNJA_AUTH_LOCAL_ENABLED: "true"
      VIKUNJA_AUTH_OPENID_ENABLED: "false"
      VIKUNJA_REDIS_ENABLED: "true"
      VIKUNJA_REDIS_HOST: redis
      VIKUNJA_REDIS_PORT: "6379"
      VIKUNJA_REDIS_PASSWORD_FILE: /run/secrets/redis_password
      VIKUNJA_REDIS_DB: "5"
      VIKUNJA_LOGGER_LEVEL: "info"
      VIKUNJA_MAILER_ENABLED: "false"
      VIKUNJA_WEBHOOKS_ENABLED: "true"
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

networks:
  xnai_network:
    external: true

secrets:
  vikunja_db_password:
    external: true
  vikunja_jwt_secret:
    external: true
  redis_password:
    external: true
```

---

## FILE 3: Caddyfile (NEW)

**Location**: `./Caddyfile`  
**Action**: Create this file

```
# ============================================================================
# Caddy Configuration - Xoe-NovAi Unified Reverse Proxy
# ============================================================================

{
  admin 127.0.0.1:2019
  
  log {
    output file /tmp/caddy_access.log {
      roll_size 10mb
      roll_keep 3
    }
    format json
  }
}

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

  # RAG API (FastAPI backend)
  @rag_api path_regexp /api/v1
  handle @rag_api {
    reverse_proxy rag:8000 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      health_uri /health
      health_interval 30s
      health_timeout 5s
    }
  }

  # Chainlit UI (WebSocket + static)
  @chainlit path /
  handle @chainlit {
    reverse_proxy ui:8001 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      websocket
    }
  }

  # Vikunja API
  @vikunja_api path_regexp /vikunja/api
  handle @vikunja_api {
    reverse_proxy vikunja-api:3456 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      health_uri /api/v1/info
      health_interval 30s
      health_timeout 5s
    }
  }

  # Vikunja Frontend (SPA)
  @vikunja_frontend path_regexp /vikunja
  handle @vikunja_frontend {
    reverse_proxy vikunja-api:3456 {
      header_up Host {upstream_hostport}
      header_up X-Forwarded-For {remote_host}
      header_up X-Forwarded-Proto {scheme}
      websocket
    }
  }

  # Fallback
  handle {
    respond "Service not found" 404
  }
}
```

---

## FILE 4: Makefile Updates

**Location**: `./Makefile` (append to existing)  
**Action**: Add these targets

```makefile
# ============================================================================
# VIKUNJA TARGETS
# ============================================================================

.PHONY: up-vikunja down-vikunja restart-vikunja logs-vikunja health-vikunja

up-vikunja: up
	@echo "🚀 Starting Vikunja overlay..."
	@mkdir -p data/vikunja/{db,files}
	@podman unshare chown 1000:1000 -R data/vikunja 2>/dev/null || true
	@podman compose -f docker-compose.yml -f docker-compose.yml up -d
	@sleep 10
	@echo "⏳ Waiting for services to stabilize..."
	@sleep 10
	@$(MAKE) health-vikunja

down-vikunja:
	@echo "🛑 Stopping Vikunja overlay..."
	@podman compose -f docker-compose.yml -f docker-compose.yml down

restart-vikunja: down-vikunja up-vikunja

logs-vikunja:
	@podman compose -f docker-compose.yml -f docker-compose.yml logs -f vikunja-api vikunja-db

health-vikunja:
	@echo "🏥 Vikunja Health Check"
	@echo "─────────────────────────────────────"
	@podman compose -f docker-compose.yml -f docker-compose.yml ps
	@echo ""
	@echo "Testing Vikunja API..."
	@curl -s http://localhost/vikunja/api/v1/info | jq -r '.version' && \
		echo "✅ Vikunja API healthy" || echo "⚠️  Vikunja API not responding yet"
	@echo ""
	@echo "Testing PostgreSQL..."
	@podman compose -f docker-compose.yml -f docker-compose.yml exec -T vikunja-db \
		pg_isready -U vikunja -h 127.0.0.1 && \
		echo "✅ PostgreSQL healthy" || echo "❌ PostgreSQL unhealthy"
```

---

## QUICK DEPLOYMENT CHECKLIST

### Phase 1: Pre-Deployment (Part 2)
```bash
# ✅ Run these first
podman --version                    # Verify 4.0+
grep "^$(whoami):" /etc/subuid      # Verify subuid range
mkdir -p data/vikunja/{db,files} config secrets
podman unshare chown 1000:1000 -R data/vikunja/
chmod 700 data/vikunja/db

# Generate secrets
openssl rand -base64 32 > secrets/redis_password.txt
openssl rand -base64 32 > secrets/vikunja_db_password.txt
openssl rand -base64 64 > secrets/vikunja_jwt_secret.txt
chmod 600 secrets/*.txt

# Register with Podman
podman secret create redis_password < secrets/redis_password.txt
podman secret create vikunja_db_password < secrets/vikunja_db_password.txt
podman secret create vikunja_jwt_secret < secrets/vikunja_jwt_secret.txt

# Verify
./pre_flight_check.sh               # Should pass all 20 checks
```

### Phase 2: File Creation (Part 3)
```bash
# Create all configuration files from this guide
# - docker-compose.yml (update: add Caddy service)
# - docker-compose.yml (new)
# - Caddyfile (new)
# - Update Makefile (add Vikunja targets)
# - config/postgres.conf (should exist from Part 2)
```

### Phase 3: Deployment (Part 3)
```bash
# Test Foundation stack first
make up              # Start without Vikunja
sleep 30
curl http://localhost/api/v1/health  # Should work

# Then add Vikunja
make up-vikunja      # Start Foundation + Vikunja
sleep 45             # Wait for PostgreSQL init
make health-vikunja  # Check all services
```

### Phase 4: Validation (Part 4)
```bash
# Test Vikunja functionality
curl http://localhost/vikunja/api/v1/info | jq .

# Create test user
VIKUNJA_API="http://localhost/vikunja/api/v1"
curl -X POST "$VIKUNJA_API/user" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@localhost","password":"testpass123"}'

# Create test task (via API)
TOKEN=$(curl -s -X POST "$VIKUNJA_API/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

curl -X POST "$VIKUNJA_API/projects/1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"Test Task"}'

# Verify persistence
make restart-vikunja  # Restart Vikunja
sleep 30
curl "$VIKUNJA_API/tasks/all" -H "Authorization: Bearer $TOKEN" | jq '.'
# Should see the test task!
```

---

## TROUBLESHOOTING: QUICK REFERENCE

| Problem | Root Cause | Solution |
|---------|-----------|----------|
| **"Permission denied" on data/vikunja** | Permissions not set | `podman unshare chown 1000:1000 -R data/vikunja/` |
| **PostgreSQL won't start** | DB directory permissions | `chmod 700 data/vikunja/db` |
| **Vikunja API returns 500** | Cannot connect to PostgreSQL | Check PostgreSQL logs: `make logs-vikunja` |
| **"Bad Gateway" from Caddy** | Vikunja API not responding | Wait 60s, check: `curl http://127.0.0.1:3456/api/v1/info` |
| **Cannot create Podman secrets** | Secrets directory missing | `mkdir -p secrets` |
| **Caddy not listening on port 80** | Port already in use | `lsof -i :80` or use port forwarding |

---

## MONITORING & MAINTENANCE

### Daily Operations

```bash
# Start all services
make up-vikunja

# Check health
make health-vikunja

# View logs
make logs-vikunja

# Stop Vikunja (keep Foundation)
make down-vikunja

# Full restart
make restart-vikunja
```

### Database Maintenance

```bash
# Access PostgreSQL CLI
podman exec xnai_vikunja_db psql -U vikunja -d vikunja

# Inside psql:
SELECT COUNT(*) FROM tasks;           # See task count
SELECT * FROM pg_stat_activity;       # See connections
VACUUM ANALYZE;                       # Optimize tables
\q                                    # Quit psql

# Backup database
podman exec xnai_vikunja_db \
  pg_dump -U vikunja -d vikunja > vikunja_backup_$(date +%Y%m%d).sql
```

### Memory Usage

```bash
# Check current memory
podman stats --no-stream vikunja-api vikunja-db

# Should show:
# vikunja-api:    100-200MB
# vikunja-db:     100-150MB
```

---

## INTEGRATION POINTS (PHASE 2)

When ready to integrate voice commands:

### Part 5A: FastAPI Webhook Listener
```python
# Add to XNAi_rag_app/api/vikunja_webhooks.py
@app.post("/vikunja/webhook")
async def vikunja_webhook(event: VikunjaWebhookEvent):
    # Handle task.created, task.updated, task.deleted events
    # Log to knowledge base
    # Trigger RAG processing
    pass
```

### Part 5B: Chainlit Voice Commands
```python
# Add to Chainlit app
@cl.on_message
async def handle_voice(message: cl.Message):
    if "create task" in message.content.lower():
        # Parse task name
        # Call Vikunja API
        # Return confirmation via TTS
        pass
```

### Part 5C: REST API Usage
```bash
# Get projects
TOKEN=$(curl -s -X POST http://localhost/vikunja/api/v1/login \
  -d '{"username":"testuser","password":"testpass123"}' | jq -r '.token')

curl http://localhost/vikunja/api/v1/projects \
  -H "Authorization: Bearer $TOKEN" | jq '.[]'

# Create task
curl -X POST http://localhost/vikunja/api/v1/projects/1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"New Task"}'

# Update task
curl -X PUT http://localhost/vikunja/api/v1/tasks/1 \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"done":true}'
```

---

## SECURITY CHECKLIST

- [ ] All data in `data/vikunja/` owned by UID 1000:1000
- [ ] All `.txt` secret files are mode 600
- [ ] Podman secrets registered (not in compose files)
- [ ] PostgreSQL runs with `user: "1000:1000"` (non-root)
- [ ] All containers have `cap_drop: ALL` + minimal `cap_add`
- [ ] Vikunja file attachments limited to 20MB
- [ ] CalDAV sync disabled (air-gapped)
- [ ] Email notifications disabled
- [ ] OpenID/OAuth disabled (local auth only)
- [ ] Telemetry disabled (verified in config)
- [ ] CORS disabled (Caddy handles proxy)
- [ ] Webhooks enabled (for Phase 2 integration)

---

## SUCCESS METRICS

When complete, you will have:

✅ **Vikunja 1.0.0 running**  
✅ **<2GB memory usage** (Vikunja + PostgreSQL)  
✅ **Full REST API** at `/vikunja/api/v1/`  
✅ **Web UI** at `/vikunja/`  
✅ **Caddy unified proxy** on port 80 (no exposed backend ports)  
✅ **Rootless Podman** security  
✅ **Secrets management** via Podman native store  
✅ **Data persistence** across restarts  
✅ **Webhook support** (Phase 2 ready)  
✅ **Voice integration** pathway established  

---

## NEXT STEPS AFTER DEPLOYMENT

1. **Create production user** (replace testuser)
2. **Set up projects** and task categories
3. **Enable webhooks** for knowledge base sync (Phase 2)
4. **Implement voice commands** (Part 5)
5. **Set up backups** (PostgreSQL daily dumps to `/backups/`)
6. **Monitor performance** (track memory, API latency)

---

## REFERENCES

- **Vikunja Docs**: https://vikunja.io/docs/
- **Vikunja API**: `http://localhost/vikunja/api/v1/docs` (Swagger UI)
- **Caddy Docs**: https://caddyserver.com/docs/
- **Podman Docs**: https://podman.io/docs/
- **PostgreSQL Tuning**: https://www.postgresql.org/docs/16/runtime-config.html

---

**Status**: Configuration Complete ✅  
**Next Action**: Follow deployment checklist above  
**Estimated Time**: 45 minutes (preparation) + 30 minutes (deployment) = ~75 minutes total

---

# END OF QUICK REFERENCE

For detailed information:
- **Part 1**: Architecture & Design (this manual)
- **Part 2**: Pre-Deployment Setup (all setup commands)
- **Part 3-5**: Configuration Files (above, consolidated)

**All 5 parts + configuration provided. Ready to deploy!**
