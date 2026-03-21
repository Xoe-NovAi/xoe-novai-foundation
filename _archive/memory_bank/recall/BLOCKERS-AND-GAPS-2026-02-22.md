# XNAi Foundation — Blockers & Knowledge Gaps
**Status Report | 2026-02-22 | Cline Session**

---

## 🔴 CRITICAL BLOCKERS

### BLOCKER-001: OpenPipe Integration — ✅ RESOLVED
| Aspect | Status | Details |
|--------|--------|---------|
| **Config File** | ✅ EXISTS | `config/openpipe-config.yaml` (3843 bytes) |
| **Dashboard** | ✅ EXISTS | `monitoring/grafana/dashboards/openpipe-dashboard.json` (14090 bytes) |
| **Core Module** | ✅ CREATED | `app/XNAi_rag_app/core/openpipe_integration.py` |
| **Docker Service** | ✅ ADDED | `openpipe` service added to `docker-compose.yml` |
| **Enhanced Init** | ✅ READY | `services_init_enhanced.py` can now import module |

**Resolution**: Core module created with SovereignOpenPipeClient, OpenPipeManager, caching, deduplication, and circuit breaker. Docker service added with 1GB memory limit, Redis dependency, and sovereign mode configuration.

**Remaining**: End-to-end testing when stack is deployed.

---

### BLOCKER-002: asyncio Violations (19 instances)
| Location | Count | Severity |
|----------|-------|----------|
| `app/XNAi_rag_app/` | 19 | HIGH |

**Impact**: Violates AGENTS.md mandate to use AnyIO TaskGroups only.

**Pattern Found**: `health_monitoring.py` explicitly uses `asyncio.create_task()` with TODO comment:
```python
import asyncio  # Still needed for Task type and create_task (migrate to TaskGroups later)
```

**Remediation Required**: Migrate all 19 instances to `anyio.create_task_group()` pattern.

---

## 🟠 HIGH PRIORITY GAPS

### GAP-001: Torch Import Status
| Check | Result |
|-------|--------|
| `import torch` in app/ | ✅ NONE FOUND |
| `from torch` in app/ | ✅ NONE FOUND |
| Torch-free mandate | ✅ COMPLIANT |

**Status**: Torch-free mandate is RESPECTED. Previous report of torch import at line 227 was FALSE POSITIVE.

---

### GAP-002: Research Queue Items (from ADDITIONAL-RESEARCH-NEEDED.md)
| ID | Priority | Topic | Status |
|----|----------|-------|--------|
| R1 | 🔴 CRITICAL | Cline 400K context window | PENDING |
| R2 | 🔴 CRITICAL | Qdrant collection state | PENDING |
| R3 | 🟠 HIGH | Antigravity complete model list | PENDING |
| R4 | 🟠 HIGH | OpenCode → Antigravity migration | PENDING |
| R5 | 🟠 HIGH | Redis Sentinel vs Standalone | PENDING |
| R6 | 🟠 HIGH | fastembed + ONNX compat | PENDING |
| R7 | 🟠 HIGH | Gemini 3 CLI availability | PENDING |
| R8-R15 | 🟡/🟢 | Medium/Low priority | PENDING |

---

## 🟢 VERIFIED WORKING

| Component | Status | Evidence |
|-----------|--------|----------|
| Torch-free codebase | ✅ CLEAN | No torch imports in app/ |
| zRAM memory | ✅ ACTIVE | 16GB, 4.1:1 compression |
| MCP Server | ✅ IMPLEMENTED | Memory Bank MCP server |
| Grafana Dashboards | ✅ COMPLETE | Week 2 observability |
| VictoriaMetrics | ✅ FOUNDATION | Week 1 metrics |
| Health Monitoring | ✅ WORKING | Uses pynvml (torch-free) |

---

## UNCOMMITTED CHANGES SUMMARY

### Deleted Files (AWQ Removal Started)
- `Dockerfile.awq`
- `app/XNAi_rag_app/core/awq_quantizer.py`
- `tests/test_awq_exceptions.py`

### Modified Files
- `.env.example`, `README.md`, `activeContext.md`, `progress.md`, `mkdocs.yml`

### Untracked Files (50+)
- OpenPipe docs (Blueprint, Guide, Summary, Analysis)
- ADRs (0005, 0006, 0007)
- Model research (Big Pickle, GPT-5 Nano, OpenCode Matrix)
- MCP server (`mcp-servers/memory-bank-mcp/`)
- Grafana dashboard (`openpipe-dashboard.json`)

---

## REMEDIATION PRIORITY ORDER

1. **BLOCKER-001**: Create missing `openpipe_integration.py` module
2. **BLOCKER-001**: Add OpenPipe service to docker-compose.yml
3. **BLOCKER-002**: Migrate 19 asyncio violations to AnyIO TaskGroups
4. **GAP-R1/R2**: Execute CRITICAL research items
5. **Commit AWQ Removal**: Stage and commit deleted files
6. **Stage Untracked**: Add all new documentation

---

**Last Updated**: 2026-02-22
**Next Review**: After blocker remediation