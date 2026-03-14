# XNAi Foundation — Comprehensive Strategy Document

**Created**: 2026-02-27  
**Status**: ACTIVE - Memory Crisis Investigation  
**Priority**: CRITICAL  

---

## Executive Summary

The XNAi Foundation system is experiencing a **critical memory crisis**:
- Physical RAM: 85% full (15% / ~2.4GB remaining on 16GB system)
- zRAM Swap: **11.3GB in use** (designed for ~12GB capacity)
- OpenCode alone: 2GB RAM usage

This document captures all discovered issues, planned fixes, and prioritization for the memory crisis resolution.

---

## Current Issues Discovered

### 1. IDE & CLI Tool Memory Issues

| Tool | Issue | Status | Documentation |
|------|-------|--------|--------------|
| OpenCode | Progressive memory growth (500MB → 2GB+) | TRACKED | `docs/reference/IDE-CLI-KNOWN-ISSUES.md` |
| VSCodium | Extension host crashes (OOM) | TRACKED | `docs/reference/IDE-CLI-KNOWN-ISSUES.md` |
| VS Code Insiders | Context window discrepancy (192K vs 264K) | INVESTIGATING | `docs/reference/IDE-CLI-KNOWN-ISSUES.md` |
| Copilot Extension | Memory exhaustion | KNOWN | `docs/reference/IDE-CLI-KNOWN-ISSUES.md` |

### 2. Redis Integration (SPLIT TEST)

| Issue | Root Cause | Status |
|-------|------------|--------|
| Authentication fails | `secrets/redis_password.txt` is EMPTY | ❌ BROKEN |
| MISCONF error | RDB persistence failing (permission/directory issue) | ❌ BROKEN |
| Wrong host | `.env` has `REDIS_HOST=redis` (docker internal) | ❌ BROKEN |

**Fix Required**:
1. Write `changeme123` to `secrets/redis_password.txt`
2. Add AOF configuration: `--appendonly yes --appendfsync everysec`
3. Add `REDIS_HOST=localhost` for local access

---

### 2. Qdrant Integration (SPLIT TEST)

| Issue | Root Cause | Status |
|-------|------------|--------|
| Vector dimension mismatch | Split test uses 64-dim hash, collection expects 384 | ❌ BROKEN |
| API errors | qdrant-client 1.13.2 vs server v1.13.1 mismatch | ❌ BROKEN |
| Collection conflicts | Creating collections without proper schema | ❌ BROKEN |

**Fix Required**:
1. Update `_simple_embedding()` to produce 384-dim vectors (or use sentence-transformers)
2. Update Qdrant calls to use `PointStruct` API
3. Add `QDRANT_HOST=localhost` for local access
4. Use existing `xnai_core` collection with correct schema

---

### 3. Docker-Compose Consolidation

| File | Purpose | Issue |
|------|---------|-------|
| `docker-compose.yml` | PRIMARY - Development stack | Good - keep |
| `docker-compose-noninit.yml` | Non-init variant | DUPLICATE - deprecate |
| `docker-compose.production.yml` | Production deployment | Legacy - keep separate |

**Fix Required**:
1. Add comments to `docker-compose.yml` explaining it's primary
2. Add deprecation notice to `docker-compose-noninit.yml`
3. Document when to use each file

---

### 4. CRITICAL: Memory Crisis

**Current State** (from btop):
- Physical RAM: 6.4 GB / 6.6 GB (**97% full**)
- zRAM Swap: **11.3 GB / 12 GB (94%)** ← OpenCode filled ENTIRE 12GB zRAM
- OpenCode Process: **1.9 GB (27.5% of system RAM)**
- Available: **218 MB**

**Root Cause**: OpenCode has a **never-ending memory leak** that progressively fills both RAM and zRAM swap until system-wide OOM occurs.

**Impact**:
- System OOM - all processes killed
- OpenCode is the primary culprit
- Risk of crashes and data loss
- Split test execution impossible under this load

---

## Memory Investigation Findings

### OpenCode Memory Usage: 2GB

**Likely Causes**:
1. Large context window loaded (200K+ tokens)
2. Session history accumulation
3. Multiple tool outputs cached
4. Memory bank loading

**Mitigation**:
- Implement context window limits
- Add session compaction
- Use memory bank sparingly
- Clear old sessions

---

### VS Code / Cline / Copilot OOM Crashes (Historical)

From log analysis:
- **VSCodium fileWatcher**: Crashed with code 15 (SIGTERM/OOM killer)
- **Cline extensionHost**: Crashed with code 133 (SIGSEGV)
- **GitHub Copilot**: Known to cause memory exhaustion in extension host

**Root Cause**: Memory pressure from AI processing + multiple extensions + large workspaces

---

### zRAM Status

From `xnai-zram-init.sh`:
- Configured: **12GB** zRAM
- Algorithm: **zstd** (good compression)
- Priority: 100
- Settings: `vm.swappiness=180`, `vm.page-cluster=0`

**Current Usage**: 11.3GB / 12GB = **94%** - CRITICAL

---

## Memory Crisis Action Plan

### IMMEDIATE ACTIONS (Now)

1. **Free Physical Memory**
   - Close unnecessary applications
   - Clear browser tabs
   - Stop unused Docker containers
   - Clear file caches

2. **Reduce OpenCode Memory**
   - Clear old sessions: `rm -rf ~/.local/share/opencode/storage/session/*`
   - Check for memory leaks
   - Limit concurrent operations

3. **Monitor with btop**
   - Run `btop` to see real-time usage
   - Focus on largest memory consumers

### SHORT-TERM (This Session)

4. **Investigate Memory Consumers**
   - Use btop to identify top processes
   - Check Docker container memory
   - Analyze OpenCode session sizes

5. **Configure Memory Limits**
   - Add memory limits to Docker Compose
   - Set VSCodium memory limits
   - Configure AI assistant context limits

6. **Fix Split Test Integration**
   - Redis: Password + AOF + localhost
   - Qdrant: 384-dim embedding + PointStruct API

### MEDIUM-TERM (Next Sessions)

7. **Prevent Future Memory Issues**
   - Set up memory monitoring alerts
   - Create memory cleanup scripts
   - Document memory management best practices
   - Implement circuit breakers for memory

---

## Technical Implementation Details

### Redis Fix (Split Test)
```bash
# Write password
echo "changeme123" > secrets/redis_password.txt

# Redis command in docker-compose (add AOF)
command: redis-server --requirepass "${REDIS_PASSWORD}" --maxmemory 512mb --maxmemory-policy allkeys-lru --appendonly yes --appendfsync everysec

# Environment for local access
REDIS_HOST=localhost
REDIS_PASSWORD=changeme123
```

### Qdrant Fix (Split Test)
```python
# Use proper embedding (384 dimensions)
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode(text)  # 384-dim

# Use PointStruct for upsert
from qdrant_client.models import PointStruct, VectorParams

# Create collection
client.create_collection(
    collection_name="xnai_core",
    vectors_config=VectorParams(size=384, distance="Cosine")
)

# Upsert points
client.upsert(
    collection_name="xnai_core",
    points=[
        PointStruct(
            id=str(uuid.uuid5(uuid.NAMESPACE_URL, f"{test_id}_{result.model_id}")),
            vector=embedding.tolist(),
            payload=result.to_dict()
        )
    ]
)
```

---

## Files to Modify

| File | Changes Required |
|------|-----------------|
| `secrets/redis_password.txt` | Write "changeme123" |
| `docker-compose.yml` | Add AOF config to Redis |
| `.env` | Add REDIS_HOST=localhost |
| `scripts/split_test/__init__.py` | Fix embedding (384-dim), fix Qdrant API |
| `configs/split-test-defaults.yaml` | Add localhost configs |
| NEW: `memory_bank/MEMORY-CRISIS-RESOLUTION.md` | Document memory fixes |

---

## Priority Order

### PRIORITY 1: Memory Crisis (CRITICAL)
1. ✅ Document state ( currentTHIS FILE)
2. ⏳ Free physical memory (user action)
3. ⏳ Investigate memory consumers
4. ⏳ Implement memory limits
5. ⏳ Set up monitoring

### PRIORITY 2: Split Test Integration
1. ⏳ Fix Redis (password + AOF + localhost)
2. ⏳ Fix Qdrant (embedding + API + localhost)
3. ⏳ Test split test execution

### PRIORITY 3: Stack Consolidation
1. ⏳ Document docker-compose files
2. ⏳ Clean up deprecated files
3. ⏳ Verify all wiring

---

## Key Configuration Values

| Service | Setting | Value |
|---------|---------|-------|
| Redis | Host | localhost |
| Redis | Port | 6379 |
| Redis | Password | changeme123 |
| Redis | Persistence | AOF (everysec) |
| Qdrant | Host | localhost |
| Qdrant | Port | 6333 |
| Qdrant | Vector Size | 384 |
| Embedding | Model | all-MiniLM-L6-v2 |

---

## VS Code / AI Assistant Memory Best Practices

From research (2024-2025):

1. **Disable unused extensions** - Extensions are primary memory consumers
2. **Use "Help: Start Extension Bisect"** - Find memory-hogging extensions
3. **Limit concurrent AI operations** - Don't run multiple AI tools simultaneously
4. **Clear workspace history** - Close unused workspaces
5. **Reduce context window** - Use smaller contexts when possible
6. **Monitor with btop** - Keep an eye on memory usage

---

## Next Steps

1. **NOW**: Free physical memory (user closes apps, we investigate)
2. **NEXT**: Identify memory-hogging processes
3. **THEN**: Fix Redis/Qdrant for split test
4. **FINALLY**: Consolidate docker-compose, verify stack

---

## Coordination Keys

- **Memory Crisis**: `MEMORY-CRISIS-2026-02-27`
- **Split Test**: `WAVE-5-SPLIT-TEST-2026-02-26`
- **Stack Wiring**: `XNAI-STACK-WIRING-2026-02-27`

---

**Last Updated**: 2026-02-27
**Next Review**: After memory crisis resolved
