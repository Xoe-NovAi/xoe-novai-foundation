# Research Request: XNAi Foundation Stack Production Optimization
## Comprehensive Knowledge Gaps for Production Readiness

**Date**: February 9, 2026  
**Requestor**: Cline (Coder Agent)  
**Context**: Complete stack rebuild after architectural issues identified  
**Goal**: Production-ready deployment with optimal architecture

---

## EXECUTIVE SUMMARY

A comprehensive investigation has identified **5 critical blockers** preventing production readiness:

1. **Port 8000 conflict** between RAG API and Caddy
2. **Caddyfile misconfiguration** (wrong service names for Vikunja)
3. **Mixed secret management** (Podman secrets vs env vars)
4. **Database password mismatch** (requires nuke)
5. **Container dependency graph hangs**

This research request seeks Claude's guidance on optimal architecture decisions before rebuilding.

---

## RESEARCH QUESTION #1: Caddy Configuration for All-in-One Vikunja

### Problem

The Caddyfile references non-existent containers:
```
reverse_proxy vikunja-api:3456      # ❌ Container doesn't exist
reverse_proxy vikunja-frontend:80   # ❌ Container doesn't exist
```

Vikunja 0.24.1 is an **all-in-one image** serving both API and frontend on port 3456.

### Current Broken Configuration

**docker-compose.yml**:
```yaml
services:
  vikunja:
    container_name: xnai_vikunja
    image: vikunja/vikunja:0.24.1
    # Single container, port 3456
```

**Caddyfile**:
```
@vikunja-api { path /vikunja/api/* }
handle @vikunja-api {
  reverse_proxy vikunja-api:3456  # Wrong!
}

@vikunja-spa { path /vikunja/* }
handle @vikunja-spa {
  reverse_proxy vikunja-frontend:80  # Wrong!
}
```

### Questions

1. **Single Route Approach**: Should we use a single route for Vikunja?
   ```
   @vikunja { path /vikunja/* }
   handle @vikunja {
     reverse_proxy xnai_vikunja:3456
   }
   ```

2. **API vs Frontend Routing**: Does Vikunja 0.24.1 handle its own routing, or do we need separate matchers?

3. **Path Stripping**: Should paths be rewritten?
   - `/vikunja/api/v1/info` → Should this reach Vikunja as `/api/v1/info`?
   - Or does Vikunja expect the full path?

4. **WebSocket Support**: Does Vikunja need WebSocket proxy configuration?

### Deliverable

A working Caddyfile configuration for all-in-one Vikunja 0.24.1 with:
- Proper service name references
- Correct path handling
- WebSocket support if needed
- Health check integration

---

## RESEARCH QUESTION #2: Redis Microservice Architecture

### Current Architecture

**Single Redis Instance** (embedded in docker-compose.yml):
```yaml
redis:
  image: redis:7.4.1
  # Serves all Foundation services (DB 0-4) + Vikunja (DB 5)
```

### Questions

1. **Isolation Strategy**: Is Redis DB numbering (0-5) sufficient for production, or should we have separate Redis instances?

2. **Performance Impact**: Will one Redis instance handle:
   - Foundation RAG API caching
   - Chainlit session storage
   - Crawler job queues
   - Vikunja session storage
   - All on Ryzen 5700U with 512MB maxmemory?

3. **Failure Domain**: If Redis fails, all services lose cache/sessions. Is this acceptable?

4. **Alternative Architecture**:
   ```yaml
   # Option A: Single Redis (current)
   redis:
     image: redis:7.4.1
     # All services, DB isolation
   
   # Option B: Separate instances
   redis-foundation:
     image: redis:7.4.1
     # Foundation services only
   
   redis-vikunja:
     image: redis:7.4.1
     # Vikunja only
   ```

5. **Resource Allocation**: With 512MB maxmemory and `allkeys-lru` policy, is eviction handling correct for production?

### Deliverable

Architecture recommendation with justification:
- Single vs separate Redis instances
- Memory allocation per service
- Monitoring recommendations
- Scaling considerations

---

## RESEARCH QUESTION #3: Podman Rootless Secret Management

### Current State (MIXED)

| Service | Method | Issues |
|---------|--------|--------|
| RAG API | Podman secrets | ❌ Rootless mounting failures |
| UI | Environment vars | ✅ Works |
| Crawler | Environment vars | ✅ Works |
| Vikunja | Environment vars | ✅ Works |

### Questions

1. **Production Pattern**: What's the industry standard for secrets in rootless Podman?

2. **Options Analysis**:
   - **Option A**: Environment variables (current working solution)
     - Pros: Simple, works reliably
     - Cons: Visible in `podman inspect`, process environment
   
   - **Option B**: Bind-mounted files
     - Pros: Files not in environment
     - Cons: More complex, file permissions
   
   - **Option C**: External vault (HashiCorp Vault, etc.)
     - Pros: Enterprise-grade
     - Cons: Additional complexity, may be overkill

3. **Security Comparison**:
   - Are environment variables sufficiently secure for:
     - REDIS_PASSWORD
     - VIKUNJA_DB_PASSWORD
     - VIKUNJA_JWT_SECRET
     - API_KEY

4. **Implementation**: If using environment variables, best practices for:
   - `.env` file permissions (currently 644)
   - Variable naming conventions
   - Rotation procedures

### Deliverable

Secret management strategy with:
- Recommended approach for production
- Implementation guide
- Security justification
- Rotation procedures

---

## RESEARCH QUESTION #4: Service Dependency Architecture

### Current State

**Caddy starts independently** - no `depends_on` configuration.

```yaml
caddy:
  # No depends_on - starts immediately
```

### Potential Issue

Caddy may start before backend services are ready, causing:
- Initial 502 errors
- Health check failures
- Poor startup experience

### Questions

1. **Dependency Strategy**: Should Caddy depend_on all services?
   ```yaml
   caddy:
     depends_on:
       rag:
         condition: service_healthy
       ui:
         condition: service_healthy
       vikunja:
         condition: service_healthy
   ```

2. **Startup Order**: What's the optimal startup sequence?
   ```
   Phase 1: Infrastructure
     - Redis
     - PostgreSQL (vikunja-db)
   
   Phase 2: Application Services
     - RAG API
     - Vikunja
   
   Phase 3: Frontend & Proxy
     - Chainlit UI
     - Caddy
   ```

3. **Health Check Timing**: Current health checks have `start_period: 30s`. Is this sufficient for all services?

4. **Circular Dependencies**: Are there any risks with adding dependencies?
   - Vikunja depends on PostgreSQL
   - Caddy depends on Vikunja
   - Any circular risks?

### Deliverable

Dependency graph recommendation:
- Complete depends_on configuration
- Startup phase strategy
- Health check tuning
- Rollback considerations

---

## RESEARCH QUESTION #5: Resource Limits for Ryzen 5700U Production

### Current Resource Configuration

```yaml
rag:
  cpuset: "0,2,4,6,8,10,12,14"  # Even cores
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

ui:
  cpuset: "1,3,5,7,9,11,13,15"  # Odd cores
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

### Questions

1. **CPU Allocation**: Is hardware steering (even/odd cores) optimal, or should we use:
   - NUMA-aware allocation?
   - Different core counts per service?
   - Let Linux scheduler handle it?

2. **Memory Limits**: With 8GB system RAM, current allocation:
   - RAG: 4GB
   - UI: 2GB
   - Other services: minimal
   - Total: ~6.5GB
   - **Is 1.5GB headroom sufficient?**

3. **Swap Configuration**: `memswap_limit: 4g` equals `mem_limit`. Should swap be:
   - Disabled (equal limits)?
   - Larger (2x memory)?
   - Smaller (0.5x memory)?

4. **Vikunja Resources**: Currently no limits set. Should we add:
   ```yaml
   vikunja:
     mem_limit: 512m
     cpus: '0.5'
   ```

5. **OOM Behavior**: With these limits, what's the OOM killer priority? Will critical services survive?

### Deliverable

Resource allocation strategy:
- CPU core assignment rationale
- Memory limits per service
- Swap configuration
- OOM priority recommendations

---

## RESEARCH QUESTION #6: Port Exposure Strategy

### Current Issues

**Port 8000 Conflict**:
```yaml
# docker-compose.yml
rag:
  ports:
    - "8000:8000"  # ❌ Exposes externally

caddy:
  ports:
    - "8000:8000"  # ❌ Same port!
```

### Proposed Solution

```yaml
rag:
  # No ports - internal only
  # Caddy proxies to rag:8000
```

### Questions

1. **External Port Strategy**: Should ANY services expose ports directly, or should Caddy be the sole entry point?

2. **Current Exposed Ports**:
   | Service | External | Should Change? |
  |---------|----------|----------------|
   | Caddy | 8000 | ✅ Keep - entry point |
   | RAG API | 8000, 8002 | ❌ Remove 8000, keep 8002? |
   | Chainlit | 8001 | ❌ Remove? |
   | MkDocs | 8008 | ⚠️ Optional |

3. **Metrics Port (8002)**: RAG API exposes metrics on 8002. Should this:
   - Remain exposed for Prometheus?
   - Be proxied through Caddy at `/metrics`?
   - Be internal only?

4. **Debug/Development**: Should we have a `docker-compose.override.yml` for development that exposes ports directly?

### Deliverable

Port strategy document:
- Which ports to expose
- Which to keep internal
- Caddy routing configuration
- Development vs production differences

---

## RESEARCH QUESTION #7: Production Monitoring & Observability

### Current State

- Prometheus metrics endpoint on RAG API (port 8002)
- Caddy access logs in JSON format
- Health checks on most services
- **No centralized monitoring stack**

### Questions

1. **Monitoring Stack**: Should we add:
   - Prometheus (metrics collection)
   - Grafana (visualization)
   - Loki (log aggregation)
   - AlertManager (alerts)

2. **Metrics to Track**:
   - Container resource usage
   - Service response times
   - Error rates
   - Redis memory usage
   - PostgreSQL connections

3. **Log Aggregation**: Currently logs go to:
   - `./logs/caddy/` (Caddy)
   - `./app/XNAi_rag_app/logs/` (RAG)
   - Container stdout/stderr
   
   Should we centralize with Loki or Fluentd?

4. **Health Check Dashboard**: Should we have a `/health` endpoint that aggregates all service health?

### Deliverable

Monitoring architecture recommendation:
- Which tools to deploy
- Metrics to collect
- Dashboard requirements
- Alert thresholds

---

## SUMMARY OF KNOWLEDGE GAPS

| # | Topic | Impact | Priority |
|---|-------|--------|----------|
| 1 | Caddy/Vikunja routing | **Complete blocker** | 🔴 Critical |
| 2 | Redis architecture | Performance/scaling | 🟡 High |
| 3 | Secret management | Security | 🟡 High |
| 4 | Service dependencies | Startup reliability | 🟡 High |
| 5 | Resource limits | Performance/stability | 🟡 High |
| 6 | Port strategy | Security/correctness | 🔴 Critical |
| 7 | Monitoring | Operations | 🟢 Medium |

---

## REQUESTED DELIVERABLES

For each research question, please provide:

1. **Recommendation**: Clear best practice advice
2. **Rationale**: Why this approach is optimal
3. **Implementation**: Specific configuration/code
4. **Alternatives**: Other options considered
5. **Trade-offs**: Pros/cons of each approach

---

## CONTEXT FOR CLAUDE

### What We Know Works
- Environment variables for secrets (reliably)
- Rootless Podman with user 1001:1001
- xnai_network for service communication
- Health checks with reasonable timeouts

### What We're Fixing
- Port 8000 conflict (removing RAG external exposure)
- Caddyfile service names (updating to actual container names)
- Mixed secret management (standardizing to env vars)
- Database state (nuking and rebuilding)

### Production Requirements
- Single entry point (Caddy on port 8000)
- No direct service exposure
- Redis isolation (decide: DB numbering vs separate instances)
- Resource optimization for Ryzen 5700U
- Monitoring capability
- Security hardening

---

## NEXT STEPS AFTER RESEARCH

1. Receive Claude's recommendations
2. Update all configuration files
3. Execute nuke plan
4. Deploy with corrected architecture
5. Verify all services accessible
6. Document final architecture

---

**END OF RESEARCH REQUEST**

**Files for Reference**:
- `COMPREHENSIVE_STACK_INVESTIGATION.md` - Full analysis
- `docker-compose.yml` - Foundation stack
- `docker-compose.yml` - Vikunja stack
- `Caddyfile` - Reverse proxy config
- `.env` - Environment variables
