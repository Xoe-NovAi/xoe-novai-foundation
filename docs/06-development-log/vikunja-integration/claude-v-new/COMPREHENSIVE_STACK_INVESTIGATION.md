# Comprehensive Stack Architecture Investigation
## XNAi Foundation + Vikunja Integration - Full Analysis

**Date**: February 9, 2026  
**Investigator**: Cline (Coder Agent)  
**Status**: CRITICAL ISSUES IDENTIFIED - RECOMMENDATION: COMPLETE REBUILD  
**Classification**: Production Readiness Review

---

## EXECUTIVE SUMMARY

### Current State: UNSTABLE ❌

Multiple critical architectural issues have been identified that prevent the stack from achieving production readiness:

1. **Port Conflicts**: Port 8000 collision between services
2. **Caddyfile Misconfiguration**: References non-existent containers
3. **Secret Management Inconsistency**: Mixed Podman secrets and env vars
4. **Network Architecture**: Partially broken dependency graph
5. **Service Discovery**: Caddy routes point to wrong service names

### Recommendation: COMPLETE NUCLEAR REBUILD

All services need to be stopped, all data purged, and stack redeployed with corrected configurations.

---

## 1. PORT ALLOCATION ANALYSIS

### Current Port Mappings

| Service | Internal Port | External Port | Host Binding | Status |
|---------|--------------|---------------|--------------|--------|
| **Caddy** | 8000 | 8000 | 0.0.0.0 | ✅ Main entry point |
| **RAG API** | 8000 | 8000 | 0.0.0.0 | ❌ **CONFLICT with Caddy** |
| **RAG API** | 8002 | 8002 | 0.0.0.0 | ✅ Metrics port |
| **Chainlit UI** | 8001 | 8001 | 0.0.0.0 | ✅ UI port |
| **MkDocs** | 8000 | 8008 | 0.0.0.0 | ⚠️ Different external port |
| **Redis** | 6379 | - | Internal only | ✅ No external exposure |
| **Vikunja** | 3456 | - | Internal only | ✅ No external exposure |
| **PostgreSQL** | 5432 | - | Internal only | ✅ No external exposure |

### Critical Port Conflict

**ISSUE**: RAG API exposes port 8000 externally, but Caddy also binds to 8000

```yaml
# docker-compose.yml (RAG Service)
ports:
  - "8000:8000"  # ❌ Conflicts with Caddy

# docker-compose.yml (Caddy Service)  
ports:
  - "8000:8000"  # ❌ Same port!
```

**Impact**: Whichever service starts second fails to bind to port 8000

---

## 2. CADDYFILE ROUTING ANALYSIS

### Current Routes (Caddyfile)

```
:8000 {
  # Foundation RAG API
  @rag-api { path /api/v1* }
  handle @rag-api {
    reverse_proxy rag:8000  # ✅ Correct
  }

  # Foundation Chainlit UI
  @foundation-ui { path / path /chainlit* }
  handle @foundation-ui {
    reverse_proxy ui:8001  # ✅ Correct
  }

  # Vikunja API
  @vikunja-api { path /vikunja/api/* }
  handle @vikunja-api {
    reverse_proxy vikunja-api:3456  # ❌ WRONG SERVICE NAME!
  }

  # Vikunja SPA
  @vikunja-spa { path /vikunja/* }
  handle @vikunja-spa {
    reverse_proxy vikunja-frontend:80  # ❌ WRONG SERVICE NAME!
  }
}
```

### Critical Issues

| Route | Current Target | Actual Service Name | Status |
|-------|---------------|---------------------|--------|
| Vikunja API | `vikunja-api:3456` | `xnai_vikunja:3456` | ❌ **BROKEN** |
| Vikunja SPA | `vikunja-frontend:80` | `xnai_vikunja:3456` | ❌ **BROKEN** |

**Problem**: Caddyfile references non-existent containers:
- `vikunja-api` does not exist (actual: `xnai_vikunja`)
- `vikunja-frontend` does not exist (actual: `xnai_vikunja`)

Vikunja 0.24.1 is an **all-in-one image** serving both API and frontend on port 3456.

---

## 3. SERVICE ARCHITECTURE ISSUES

### 3.1 RAG API Port Exposure

**Current (BROKEN)**:
```yaml
rag:
  ports:
    - "8000:8000"  # Exposes externally
```

**Should Be (FIXED)**:
```yaml
rag:
  ports:
    - "8000"  # Internal only, Caddy proxies
```

RAG API should NOT bind to host port 8000 - Caddy should be the sole external entry point.

### 3.2 Secret Management Inconsistency

**Current State - MIXED MODES**:

| Service | Secrets Method | Status |
|---------|---------------|--------|
| RAG API | Podman secrets (`/run/secrets/`) | ❌ Rootless issues |
| UI | Environment variables | ✅ Works |
| Crawler | Environment variables | ✅ Works |
| Curation | Environment variables | ✅ Works |
| Vikunja | Environment variables | ✅ Works (after fix) |

**Recommendation**: Standardize on environment variables for all services (Claude's recommendation)

### 3.3 Redis Architecture Question

**Current**: Redis is embedded in main docker-compose.yml

**Question**: Should Redis have its own microservice yaml file?

**Analysis**:
- ✅ **Keep embedded**: Redis is core infrastructure, required by multiple services
- ✅ **Single source of truth**: One Redis instance serves all services
- ✅ **DB isolation**: Uses Redis DB numbers (0-4 Foundation, 5 Vikunja)
- ⚠️ **Alternative**: Separate yaml only if Redis needs independent scaling

**Verdict**: Keep Redis in main compose. It's properly isolated via database numbers.

---

## 4. NETWORK ARCHITECTURE

### Network Configuration

```yaml
# docker-compose.yml
networks:
  xnai_network:
    driver: bridge
    name: xnai_network

# docker-compose.yml
networks:
  xnai_network:
    external: true  # ✅ Correct - references existing
```

### Service Dependencies

```
Caddy (entry point)
├── RAG API (depends_on: redis)
├── Chainlit UI (depends_on: redis, rag)
├── Crawler (depends_on: redis, rag)
├── Curation Worker (depends_on: redis)
├── MkDocs (standalone)
├── Redis (base service)
├── Vikunja (depends_on: vikunja-db)
└── PostgreSQL (vikunja-db)
```

### Dependency Chain Issues

1. **Vikunja is isolated** - No dependencies on Foundation services (good)
2. **Caddy doesn't depend on services** - May start before backends ready
3. **Circular dependency risk** - None detected

---

## 5. SECURITY ANALYSIS

### Current Security Posture

| Aspect | Status | Notes |
|--------|--------|-------|
| Rootless containers | ✅ | User 1001:1001 |
| No-new-privileges | ✅ | Most services |
| Capability dropping | ✅ | `cap_drop: ALL` |
| Read-only filesystems | ⚠️ | Partial |
| tmpfs for temp | ✅ | Sensitive dirs |
| Secrets in env | ⚠️ | Mixed (needs standardization) |
| Network isolation | ✅ | xnai_network |
| Port exposure | ❌ | RAG API exposes 8000 externally |

---

## 6. CRITICAL ISSUES SUMMARY

### Blocker #1: Port 8000 Conflict 🔴
**Impact**: Services cannot start simultaneously  
**Fix**: Remove `ports:` from RAG API, use internal only

### Blocker #2: Caddyfile Wrong Service Names 🔴
**Impact**: Vikunja completely inaccessible via proxy  
**Fix**: Update Caddyfile to use `vikunja:3456` (single service)

### Blocker #3: Podman Secrets in Rootless Mode 🔴
**Impact**: Secret mounting failures, auth errors  
**Fix**: Convert all secrets to environment variables

### Blocker #4: Database Password Mismatch 🟡
**Impact**: Vikunja cannot authenticate to PostgreSQL  
**Fix**: Nuclear reset of database with correct password

### Blocker #5: Container Dependency Graph Hang 🟡
**Impact**: podman-compose hangs during deployment  
**Fix**: Clean container state, restart fresh

---

## 7. OPTIMAL ARCHITECTURE RECOMMENDATIONS

### 7.1 Service Wiring Optimization

**Current Issues**:
- Too many exposed ports
- Inconsistent secret management
- Caddy misconfigured

**Recommended Architecture**:

```
┌─────────────────────────────────────────┐
│           Caddy (Port 8000)             │
│         (Single Entry Point)            │
└─────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌───────┐    ┌────────┐    ┌──────────┐
│  RAG  │    │  UI    │    │ Vikunja  │
│ :8000 │    │ :8001  │    │  :3456   │
└───────┘    └────────┘    └──────────┘
    │              │              │
    └──────────────┼──────────────┘
                   │
            ┌──────────┐
            │  Redis   │
            │  :6379   │
            └──────────┘
                   │
            ┌──────────┐
            │PostgreSQL│
            │  :5432   │
            └──────────┘
```

### 7.2 Port Strategy

| Service | External | Internal | Notes |
|---------|----------|----------|-------|
| Caddy | 8000 | 8000 | Only external port |
| RAG API | - | 8000 | Internal only |
| Chainlit | - | 8001 | Internal only |
| Vikunja | - | 3456 | Internal only |
| MkDocs | 8008 | 8000 | Documentation (optional) |

### 7.3 Secret Management Strategy

**Standardize on Environment Variables**:

```yaml
# All services use this pattern:
environment:
  - REDIS_PASSWORD=${REDIS_PASSWORD}
  - API_KEY=${API_KEY}
  - VIKUNJA_DB_PASSWORD=${VIKUNJA_DB_PASSWORD}
```

**Remove all Podman secrets** from docker-compose files.

---

## 8. COMPLETE NUKE PLAN

### Step 1: Stop All Containers
```bash
podman stop -a
podman rm -a
```

### Step 2: Purge All Data
```bash
sudo rm -rf ./data/redis/*
sudo rm -rf ./data/vikunja/*
sudo rm -rf ./data/faiss_index/*
sudo rm -rf ./data/prometheus-multiproc/*
# Keep ./library and ./knowledge if needed
```

### Step 3: Remove Images (Optional)
```bash
podman rmi -a
```

### Step 4: Reset Network
```bash
podman network rm xnai_network
podman network create xnai_network
```

### Step 5: Verify Clean State
```bash
podman ps -a  # Should show no containers
podman images  # Should show minimal images
```

---

## 9. REDEPLOYMENT PLAN

### Phase 1: Fix Configuration Files
1. Update docker-compose.yml (remove RAG port 8000)
2. Update Caddyfile (fix Vikunja service names)
3. Standardize all secrets to env vars
4. Verify .env has all required passwords

### Phase 2: Deploy Foundation Stack
```bash
podman-compose -f docker-compose.yml up -d
```

### Phase 3: Deploy Vikunja Stack
```bash
podman-compose -f docker-compose.yml -f docker-compose.yml up -d
```

### Phase 4: Verify
```bash
curl http://localhost:8000/api/v1/health  # RAG API
curl http://localhost:8000/vikunja/api/v1/info  # Vikunja
```

---

## 10. RESEARCH REQUESTS

### Knowledge Gap #1: Caddy Configuration for Single Vikunja Container
**Question**: How should Caddyfile route to all-in-one Vikunja image?

Current broken config:
```
reverse_proxy vikunja-api:3456  # Wrong
reverse_proxy vikunja-frontend:80  # Wrong
```

Need correct configuration for single container serving both API and SPA.

### Knowledge Gap #2: Redis Isolation Strategy
**Question**: Is Redis DB numbering (0-5) sufficient isolation for production?

Current:
- DB 0-4: Foundation services
- DB 5: Vikunja

Should Vikunja have separate Redis instance?

### Knowledge Gap #3: Podman Rootless Secret Alternatives
**Question**: What's the production-ready pattern for secret management in rootless Podman?

Options:
1. Environment variables (current fix)
2. Bind-mounted secret files
3. External secret management (HashiCorp Vault, etc.)

### Knowledge Gap #4: Health Check Dependencies
**Question**: Should Caddy depend_on all backend services?

Current: Caddy starts independently
Potential issue: Caddy may proxy to not-yet-ready services

### Knowledge Gap #5: Resource Limits for Production
**Question**: What are optimal resource limits for Ryzen 5700U production deployment?

Current limits may not be optimized for production workload.

---

## 11. FILES REQUIRING MODIFICATION

| File | Changes Required | Priority |
|------|-----------------|----------|
| docker-compose.yml | Remove RAG port 8000, convert secrets | 🔴 Critical |
| Caddyfile | Fix Vikunja service names | 🔴 Critical |
| docker-compose.yml | Standardize env vars | 🟡 High |
| .env | Verify all passwords present | 🟡 High |
| config.toml | Verify service endpoints | 🟢 Medium |

---

## 12. MA'AT ALIGNMENT ASSESSMENT

| Principle | Current State | Target |
|-----------|--------------|--------|
| **Modularity** | ⚠️ Services coupled via ports | ✅ Clean separation |
| **Truth** | ❌ Caddyfile lies about services | ✅ Accurate config |
| **Balance** | ⚠️ Mixed secret strategies | ✅ Unified approach |
| **Security** | ⚠️ Ports exposed unnecessarily | ✅ Minimal exposure |
| **Harmony** | ❌ Services conflict | ✅ Cooperative system |

---

## CONCLUSION

### Immediate Actions Required

1. **NUKE**: Complete purge of all containers and data
2. **FIX**: Update configuration files (docker-compose.yml, Caddyfile)
3. **STANDARDIZE**: All secrets to environment variables
4. **REBUILD**: Deploy with corrected architecture
5. **VERIFY**: All services accessible via Caddy proxy

### Estimated Time to Production Readiness
- **Investigation**: ✅ Complete
- **Configuration fixes**: 30 minutes
- **Nuke and rebuild**: 15 minutes
- **Verification**: 15 minutes
- **Total**: ~1 hour

### Success Criteria
- [ ] All containers start without port conflicts
- [ ] Caddy routes all traffic correctly
- [ ] No secret mounting errors
- [ ] Vikunja accessible at /vikunja
- [ ] Foundation API accessible at /api/v1
- [ ] All health checks passing

---

**END OF INVESTIGATION**

**Next Step**: Execute nuke plan and rebuild with corrected configurations.
