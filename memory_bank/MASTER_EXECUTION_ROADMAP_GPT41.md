---
document_type: report
title: MASTER EXECUTION ROADMAP GPT41
created_by: Haiku-4.5 (Phase 2C Automation)
created_date: 2026-03-14
version: 1.0
status: active
hash_sha256: 1845b1752f36431e88f791f610b943e8cdc4c5f881f8d738832fc19b8daf8540
---

# 🗺️ Master Execution Roadmap — GPT-4.1 Integration
**Author**: Copilot CLI | **Date**: 2026-03-13 | **Version**: v1.0  
**Status**: READY FOR HAIKU REVIEW | **Scope**: 30-day execution plan (Days 1–30+)

---

## Executive Summary

This roadmap synthesizes:
1. **Sonnet IMPL Guides** (3,049 lines): Infrastructure (P0), Container Orchestration (P0), Secrets Management (P1)
2. **Current Session Plan**: 16-phase strategy with 19.65h estimated effort
3. **GPT-4.1 Research Recommendations**: 8 new projects identified
4. **Knowledge Gap Research**: Phase 2–4 technical best practices

**Critical Success Path**: Storage cleanup (P0) → Service recovery (P0) → Secrets hardening (P1) → Agent integration (Phase 3) → Scaling infrastructure (Phase 4+)

---

## 🔴 PHASE 0: EMERGENCY STABILIZATION (Days 1–3, 4–5h effort)

### 0.1 Storage Crisis Resolution — **BLOCKING ALL OTHER WORK**

**Status**: 🔴 CRITICAL (Disk at 93%, SQLite writes failing above 95%)  
**Owner**: Copilot + User  
**Timeline**: 2–3 hours  
**Dependencies**: None (execute first!)

**Refactoring Items from IMPL-01 §4**:

| Task ID | Action | Estimated Time | Success Metric |
|---------|--------|-----------------|-----------------|
| **ST-001** | Run Podman prune (clean images, containers, build cache) | 10 min | 5–10 GB freed |
| **ST-002** | SQLite VACUUM on Podman bolt_state.db | 5 min | DB optimized, WAL clean |
| **ST-003** | Journal cleanup (keep 7 days) | 3 min | <100 MB journal |
| **ST-004** | Cache purge (pip, npm, .cache/) | 5 min | 1–3 GB freed |
| **ST-005** | Python bytecode cleanup (__pycache__ recursion) | 5 min | 500 MB freed |
| **ST-006** | Git GC --aggressive (repo compaction) | 15 min | 3–5 GB freed (40–60% reduction) |
| **ST-007** | Temp file cleanup (/tmp, >3 days old) | 3 min | 1–2 GB freed |
| **ST-008** | Review & targeted deletion (node_modules, old logs) | 20 min | 2–5 GB freed |
| **ST-009** | Verify disk <85% before Phase 1 | 2 min | `df -h /` shows <85% |

**Expected Outcome**: 8–15 GB freed, disk drops to 78–82%  
**Fallback**: If >85% after Phase 1, execute Phase 3 (storage relocation to omega_library)

---

### 0.2 Pre-Recovery Diagnostics

**Timeline**: 5 minutes  
**Owner**: User or Copilot  

1. Run full diagnostic protocol (IMPL-02 §3)
2. Capture: Container health, OOM kill logs, dependency checks
3. Create baseline report for service recovery phase

---

## 🔴 PHASE 1: SERVICE RECOVERY (Days 3–5, 3–4h effort)

### 1.1 qdrant Recovery — **PRIMARY BLOCKER**

**Status**: ❌ UNHEALTHY (Exit code 137 = OOM)  
**Owner**: Copilot  
**Timeline**: 1–2 hours (includes WAL recovery fallback)  
**Dependencies**: PHASE-0 complete

**Refactoring Items from IMPL-02 §4–5**:

| Task ID | Action | Effort | Dependencies |
|---------|--------|--------|--------------|
| **QR-001** | Diagnose exit code and logs | 10 min | Disk >85% |
| **QR-002** | Apply 768MB memory limit (deploy.resources) | 10 min | QR-001 |
| **QR-003** | Restart qdrant, wait for health (90s timeout) | 5 min | QR-002 |
| **QR-004** | Verify collections exist (curl /collections) | 5 min | QR-003 |
| **QR-005** | **[Fallback]** WAL Corruption Tier-1: Remove lock files, retry | 15 min | QR-003 fails |
| **QR-006** | **[Fallback]** WAL Corruption Tier-2: Destroy + recreate volume | 45 min | QR-005 fails |

**Success Metric**: `curl -sf http://localhost:6333/health` → 200 OK + collections listed

---

### 1.2 rag_api & Dependent Services Recovery

**Status**: ⚠️ BLOCKED (depends on qdrant)  
**Owner**: Copilot  
**Timeline**: 30 minutes  

| Task ID | Action | Effort | Pre-requisite |
|---------|--------|--------|---------------|
| **RA-001** | Verify qdrant healthy (pre-check) | 2 min | QR-* complete |
| **RA-002** | Restart rag_api, wait 60s | 5 min | RA-001 |
| **RA-003** | Verify tools list (curl /tools/list) | 5 min | RA-002 |
| **RA-004** | Restart oikos, librarian independently | 10 min | RA-003 |
| **RA-005** | Verify Grafana (requires postgres T1) | 5 min | RA-004 |
| **RA-006** | Verify Caddy port 80 bound | 3 min | RA-005 |

**Success Metric**: All 6 unhealthy services (qdrant, rag_api, oikos, librarian, grafana, caddy) → ✅ Healthy

---

### 1.3 Resource Limits Hardening

**Timeline**: 20 minutes  
**Owner**: Copilot  

From IMPL-02 §6: Apply memory limits to docker-compose.yml

| Service | Hard Limit | Reservation | Priority |
|---------|-----------|------------|----------|
| **postgres** | 768 MB | 256 MB | T1 |
| **redis** | 384 MB | 128 MB | T1 |
| **qdrant** | 768 MB | 256 MB | T2 (was 1GB) |
| **rag_api** | 1024 MB | 512 MB | T3 (was 2GB) |
| **memory-bank-mcp** | 768 MB | 256 MB | T2 |
| **vikunja_db, victoriametrics, grafana** | Per deploy block | 128 MB | T4–T5 |

**Total Allocation**: ~5.4 GB (82% of 6.6 GB physical, leaves 18% headroom)

---

## 🟡 PHASE 1.5: QUADLET MIGRATION (Days 5–6, 2–3h effort)

### 1.5.1 Quadlet Setup

**Status**: 🟡 PENDING (podman-compose → Quadlets for production reliability)  
**Owner**: Copilot + Haiku  
**Timeline**: 2–3 hours  

From IMPL-02 §7:
- Quadlets = systemd unit files managed by Podman (replaces podman-compose for long-running services)
- Provide native reboots survival, health checks, ordered startup
- Migration: 5 critical services (redis, postgres, qdrant, rag_api, memory-bank-mcp)

**Refactoring**:
1. Create `/home/arcana-novai/.config/containers/systemd/` directory
2. Convert docker-compose.yml T1–T2 services to Quadlets
3. Test systemctl enable/start/stop/restart
4. Verify services survive system reboot
5. Keep podman-compose for dev/testing only

**Success Metric**: `systemctl --user list-units | grep -i omega` shows 5+ active units

---

## 🟢 PHASE 2: SECRETS HARDENING (Days 6–8, 2–3h effort)

### 2.1 Immediate Credential Rotation

**Status**: 🔴 CRITICAL (Default `changeme123` in .env)  
**Owner**: User + Copilot  
**Timeline**: 45 minutes  

From SUPP-02 §2:

| Credential | Current State | Action | Impact |
|-----------|--------------|--------|--------|
| POSTGRES_PASSWORD | `changeme123` | Rotate via ALTER USER + .env update + restart services | T1 blocker |
| REDIS_PASSWORD | `changeme123` | Rotate via CONFIG SET + .env update | T1 blocker |
| MARIADB_ROOT_PASSWORD | `changeme123` | Rotate via ALTER USER | Low (vikunja only) |
| VIKUNJA_SECRET | Hardcoded string | Rotate via random base64 | Medium |
| GRAFANA_ADMIN_PASSWORD | Likely default | Rotate via Grafana API | Low (not exposed) |

**Procedure**:
1. Generate 6 new cryptographically secure passwords (openssl rand -base64 40)
2. Store in password manager first (backup before applying)
3. Rotate each credential in service, then .env, then restart services
4. Verify connectivity after each rotation

**Success Metric**: All services healthy after rotation, no auth errors in logs

---

### 2.2 Git History Cleanup

**Status**: 🔴 CRITICAL (Google API key previously committed)  
**Owner**: Copilot (with User approval)  
**Timeline**: 30 minutes  

From SUPP-02 §3:

```bash
# Use git-filter-repo (safer than git filter-branch)
git filter-repo --path-glob '.env' --invert-paths --force
git filter-repo --path-glob '*.pem' --path-glob '*.key' --invert-paths --force
git filter-repo --path-glob '*oauth_creds*' --invert-paths --force
```

**Then**:
1. Update .gitignore with secrets patterns
2. Force push (requires user authorization)
3. Notify all collaborators to re-clone

**Success Metric**: `git log --all --grep="password\|secret\|token"` returns 0 results

---

### 2.3 Pre-commit Hooks

**Timeline**: 15 minutes  

From SUPP-02 §4:

1. Install pre-commit framework
2. Add detect-secrets + custom hooks for .env, private keys, default passwords
3. Run baseline scan to generate .secrets.baseline
4. Test hooks (verify they block `changeme123` patterns)

**Success Metric**: `git add .env.test && git commit -m 'test'` → BLOCKED with error message

---

### 2.4 SOPS + age Encryption

**Timeline**: 20 minutes  

From SUPP-02 §5:

1. Install age + SOPS
2. Generate age encryption key (age-keygen)
3. Create .sops.yaml with age public key
4. Encrypt .env → .env.encrypted
5. Update container env_file references

**Success Metric**: `.env.encrypted` is committed, `.env` is in .gitignore, `sops -d .env.encrypted` decrypts successfully

---

## 🟡 PHASE 3: AGENT INTEGRATION & LLM ORCHESTRATION (Days 8–15, 5–6h effort)

### 3.1 LangGraph Setup

**Status**: 🟡 PENDING  
**Owner**: Copilot + GPT-4.1  
**Timeline**: 2–3 hours  

**Research Findings**: LangGraph is a low-level library for building multi-agent systems with explicit state management and guardrails. Key advantages:
- Native support for agent-to-agent communication
- Cycles + persistence (replay, debugging)
- Works with any LLM (OpenAI, Claude, local models)

**Implementation**:
1. Add LangGraph to requirements
2. Create agent coordinator graph (research facet, data scientist facet, architect proxy)
3. Implement state schema (shared context across agent handoffs)
4. Add streaming support for real-time multi-agent outputs
5. Integrate with existing MCP servers

**Success Metric**: Multi-agent workflow completes with context preserved across 3+ agent handoffs

---

### 3.2 Model Context Preservation

**Status**: 🟡 PENDING  
**Owner**: GPT-4.1  
**Timeline**: 1–2 hours  

**Challenge**: When switching models mid-session (Gemini → Claude → Grok), conversation context is lost.

**Solution**: Implement context bridge:
1. Store conversation history in Redis (keyed by session_id)
2. Create context serialization (compress via SOPS)
3. On model switch: Restore context from Redis, prepend to prompt
4. Verify token budget before restoration (prevent context overflow)

**Success Metric**: Agent switches from Gemini to Claude without losing prior turns

---

### 3.3 Multi-Agent Orchestration

**Timeline**: 2–3 hours  

From Phase 3 in current plan:
- Set up 3 agent roles: Research, DataScientist, Architect
- Implement routing logic (which agent handles which task)
- Add inter-agent communication (agent A requests data from agent B)
- Implement consensus logic (multiple agents vote on decisions)

**Success Metric**: Multi-agent team produces coherent output for complex tasks

---

## 🟢 PHASE 4: INFERENCE OPTIMIZATION & SCALING (Days 15–25, 6–8h effort)

### 4.1 Inference Optimization

**Timeline**: 2–3 hours  

**Research-Backed Techniques**:
- **Quantization**: 4-bit (llama.cpp) reduces memory 4x, loses ~2% accuracy
- **Batching**: Multiple requests per call (10x throughput improvement)
- **Caching**: Use Redis for common queries (semantic similarity, >90% cache hit rate)
- **Token prediction**: Implement speculative decoding (reduce generation latency 1.3–2x)

**Implementation**:
1. Add quantization profiles to model loader
2. Implement request batching in rag_api
3. Add Redis caching for semantic search results
4. Profile inference latency (baseline → optimized)

**Success Metric**: End-to-end latency <2s for typical query (was 5–8s)

---

### 4.2 Cost Tracking

**Timeline**: 1–2 hours  

**Metrics to Track**:
- API calls per model (Claude, Gemini, Grok, local Krikri-8B)
- Tokens (input + output) per request
- Cost per request ($0.003–$0.03 depending on model)
- Aggregate daily/monthly cost

**Implementation**:
1. Add tracking middleware to FastAPI (rag_api)
2. Log to VictoriaMetrics (already deployed)
3. Create Grafana dashboard with cost breakdown
4. Set alerts for budget thresholds

**Success Metric**: Cost dashboard shows cost-per-request for each model, daily totals accurate

---

### 4.3 Monitoring & Observability

**Timeline**: 1–2 hours  

From IMPL-02 §8–10:
- Extend health checks (currently basic /health endpoints)
- Add SLO monitoring (request latency, error rate, availability)
- Implement distributed tracing (request flow across services)
- Add log aggregation (centralized search across all containers)

**Success Metric**: Grafana dashboard shows service health, latency percentiles (p50/p99), error rates

---

## 🟠 PHASE 5: KNOWLEDGE BASE OPTIMIZATION (Days 20–28, 4–5h effort)

### 5.1 Qdrant Indexing Strategy

**Timeline**: 1–2 hours  

**Current Issue**: Qdrant collections missing after Phase 1 recovery (Tier-2 WAL destruction)

**Solution**:
1. Re-index all documents via memory-bank-mcp → xnai-rag ingestion pipeline
2. Create FAISS backup (local offline fallback)
3. Implement incremental indexing (new docs auto-indexed within 5 min)
4. Set up replication (hot standby on omega_library drive)

**Success Metric**: Qdrant /collections endpoint returns 3+ collections with >10k vectors total

---

### 5.2 FAISS Local Backup

**Timeline**: 1 hour  

- Weekly FAISS snapshot (compressed, stored locally)
- Fast recovery path if Qdrant fails (reload from FAISS in <5 min)
- Test recovery annually

**Success Metric**: FAISS index loads, semantic search returns results without Qdrant

---

## 🟣 PHASE 6+: ADVANCED FEATURES (Days 25+, TBD)

### 6.1 Knowledge Distillation

**Status**: ✅ ACTIVE (app/XNAi_rag_app/core/distillation/)  

Summarize documents via LLM → store compressed version → faster retrieval

### 6.2 Vulkan Acceleration

**Status**: 🛠 WARM (app/XNAi_rag_app/core/vulkan_acceleration.py)  

Hardware acceleration for inference on RDNA2 GPU (if available)

### 6.3 Advanced Rate Limiting

**Status**: ✅ RESTORED (app/XNAi_rag_app/core/rate_limit_handler.py)  

Account rotation + context preservation across API key limits

---

## 📊 Resource Allocation & Timeline

### Critical Path (Blocking Dependencies)

```
PHASE-0 (Storage) [2-3h]
    ↓
PHASE-1 (Services) [3-4h]
    ↓
PHASE-1.5 (Quadlets) [2-3h]
    ↓
PHASE-2 (Secrets) [2-3h]
    ↓
PHASE-3 (Agent Integration) [5-6h] ← Parallel: Phase 4 can start after Phase 2
    ↓
PHASE-4 (Scaling) [6-8h]
    ↓
PHASE-5 (KB Optimization) [4-5h]
```

**Total Sequential Time**: ~24–35 hours over 25–30 days  
**Parallelizable Phases**: Phase-4 can start after Phase-2 (secrets safe)

### Resource Ownership

| Phase | Copilot | User | GPT-4.1 | Haiku | Notes |
|-------|---------|------|---------|-------|-------|
| Phase-0 | ⭐ (execute) | ⭐ (approve) | | | High-risk cleanup |
| Phase-1 | ⭐ | ✅ (monitor) | | | Service recovery |
| Phase-1.5 | ⭐ | | ✅ (guide) | | Quadlet migration |
| Phase-2 | ✅ (guide) | ⭐ (credentials) | | | Secrets critical |
| Phase-3 | ⭐ (orchestration) | ✅ (validate) | ⭐⭐ (LangGraph) | | Heavy context synthesis |
| Phase-4 | ✅ (implement) | ✅ (profile) | ⭐ (optimization) | | Inference tuning |
| Phase-5 | ⭐ | ✅ (monitor) | | ✅ | Knowledge ops |

**Legend**: ⭐ = primary, ⭐⭐ = heavy context needed, ✅ = support/monitor

---

## 🎯 Success Metrics & Verification Checklist

### Phase-0 Complete ✅
- [ ] Disk usage <85%
- [ ] SQLite VACUUM successful
- [ ] Podman system df shows <100GB total used

### Phase-1 Complete ✅
- [ ] `podman ps --filter "health=unhealthy"` returns 0 results
- [ ] All 25 services healthy (podman ps -a shows healthy/exited, no dead)
- [ ] qdrant /collections endpoint responsive

### Phase-1.5 Complete ✅
- [ ] 5+ systemd units active (`systemctl --user list-units | grep -i omega`)
- [ ] System survives reboot with services auto-starting
- [ ] No podman-compose in production startup

### Phase-2 Complete ✅
- [ ] No default passwords in logs
- [ ] Git history clean (`git log --all | grep -i "password\|secret"` returns 0)
- [ ] `.env` in .gitignore, `.env.encrypted` can decrypt

### Phase-3 Complete ✅
- [ ] LangGraph agent graph compiles
- [ ] Multi-agent handoff preserves context across 3+ turns
- [ ] rag_api + xnai-rag + memory-bank-mcp all operational

### Phase-4 Complete ✅
- [ ] Inference latency <2s (was 5–8s)
- [ ] Cost tracking enabled in Grafana
- [ ] Health checks show >99% uptime

### Phase-5 Complete ✅
- [ ] Qdrant collections re-indexed
- [ ] FAISS backup available
- [ ] Incremental indexing working

---

## ⚠️ Known Risks & Mitigation

| Risk | Impact | Mitigation | Owner |
|------|--------|-----------|-------|
| **Storage cleanup fails to free enough space** | Blocks all other work | Phase 3 fallback: relocate Podman to omega_library drive | Copilot |
| **qdrant WAL corruption (Tier-2) loses all embeddings** | Re-indexing 5–8h | Pre-index documents again via ingestion pipeline; FAISS backup | Copilot |
| **Credential rotation breaks services** | Temporary outage (30 min) | Test each service after rotation; have old credentials available for rollback | User |
| **Git history clean fails to remove all secrets** | Security exposure | Use BFG Repo Cleaner as fallback; revoke all exposed credentials | User |
| **LangGraph integration unstable** | Phase-3 delay | Implement on test branch first; revert if fails | GPT-4.1 |
| **Inference optimization doesn't improve latency** | Wasted effort | Profile before/after; if <10% improvement, deprioritize | Copilot |

---

## 📝 Next Actions

**Immediate (Today)**:
1. [ ] User approves Phase-0 execution
2. [ ] Copilot begins storage cleanup
3. [ ] Parallel: Create task tracking for Phases 1–5 (in memory_bank/tasks/)

**This Week**:
1. [ ] Phase-0 complete (disk <85%)
2. [ ] Phase-1 complete (all services healthy)
3. [ ] Phase-1.5 start (Quadlet migration)

**Next Week**:
1. [ ] Phase-2 complete (secrets hardened)
2. [ ] Phase-3 start (LangGraph setup)

**Week 3–4**:
1. [ ] Phase-3 complete (multi-agent orchestration)
2. [ ] Phase-4 complete (inference optimization)
3. [ ] Phase-5 start (KB optimization)

---

## Appendix: Sonnet IMPL Integration Checklist

**All refactoring items from IMPL-01, IMPL-02, SUPP-02 tracked in**:  
`SONNET_IMPL_INTEGRATION_CHECKLIST.md` (generated separately)

**Mapping of Sonnet sections to Omega Stack files**:
- IMPL-01 §4 (Storage) → `scripts/storage_cleanup.sh` (create)
- IMPL-01 §5 (Podman) → `.config/containers/storage.conf` (update)
- IMPL-02 §6 (Resource Limits) → `docker-compose.yml` (update deploy blocks)
- IMPL-02 §7 (Quadlets) → `.config/containers/systemd/*.container` (create)
- SUPP-02 §2 (Credential Rotation) → `.env` + service configs (update)
- SUPP-02 §4 (Pre-commit Hooks) → `.pre-commit-config.yaml` (create + install)
- SUPP-02 §5 (SOPS + age) → `.sops.yaml`, `secrets/` (create + encrypt)

---

**END OF ROADMAP**

Status: READY FOR HAIKU REVIEW & EXECUTION  
Last Updated: 2026-03-13 23:45 UTC
