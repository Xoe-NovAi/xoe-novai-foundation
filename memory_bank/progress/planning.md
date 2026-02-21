---
block:
  label: progress_planning
  description: Next steps, roadmap, and Phase 5 planning
  chars_limit: 3000
  read_only: false
  tier: core
  priority: 2
created: 2026-02-20
modified: 2026-02-20
version: "1.0"
---

# Planning & Next Steps

## Immediate (Sprint 8) - Unified Execution Strategy

**6-Week Implementation**: MemGPT Architecture, VictoriaMetrics, Grafana, MCP, A2A

### Week 1: VictoriaMetrics Foundation (IN PROGRESS)

| # | Task | Status | Notes |
|---|------|--------|-------|
| 1.1 | VM Service Startup | ✅ Complete | Health OK, port 8428 |
| 1.2 | Memory Tools Integration | 🔄 Next | Connect metrics_collector.py |
| 1.3 | Redis + VM Split | ⏳ Pending | Real-time + historical |

### Week 2-6: Planning

| Week | Focus | Status |
|------|-------|--------|
| 2 | Grafana Dashboards | ⏳ Pending |
| 3 | MCP Server | ⏳ Pending |
| 4-5 | A2A Protocol | ⏳ Pending |
| 6 | Testing & Validation | ⏳ Pending |

### Other Sprint 8 Tasks

| # | Task | Owner | Status |
|---|------|-------|--------|
| 2 | Cognitive enhancements CE-001–CE-006 | Any Agent | From benchmark analysis |
| 3 | XNAI-STACK-OVERVIEW.md | Any | C4 Mermaid diagram |
| 4 | README.md update | Any | Project overview refresh |

## Week 2

| # | Task | Owner | Status |
|---|------|-------|--------|
| 5 | First benchmark run | Any | `./scripts/run-benchmark.sh --integrate -m gemini-3-pro` |
| 6 | FREE-AI-PROVIDERS-COMPLETE-GUIDE.md | Any | Tutorial for provider selection |
| 7 | MkDocs superfences Mermaid config | Any | Verify rendering |
| 8 | MkDocs benchmark section | Any | Add `benchmarks/` to docs nav |
| 9 | Enhanced Strategy Package Review | Opus | Review and approve for implementation |

## Month 2

| # | Task | Owner | Status |
|---|------|-------|--------|
| 10 | Multi-model benchmark results | Any | Run full 10-model battery |
| 11 | Benchmark v1.1.0 | Any | Implement CE-001 through CE-006 |
| 12 | OpenCode fork | Architect | Begin arcana-novai/opencode-xnai |
| 13 | Phase 8 planning | Any | Redis Streams, Qdrant, fine-tuning |
| 14 | Strategy Implementation | Any | Begin Tier 1 blockers (P-001 to P-004) |

---

## Phase 5 Planning

### Research Materials Generated
1. **Phase 5 zRAM Optimization Design** - Testing framework ready
2. **Build System Audit Report** - Makefile and Dockerfile analysis
3. **Claude Sonnet Research Request** - Makefile modernization, Dockerfile optimization

### Execution Schedule
- **5.A Baseline Collection**: Terminal session, clean system
- **5.B Kernel Tuning**: vm.swappiness optimization
- **5.C Stress Testing**: Concurrent load with profiling
- **5.D Analysis**: Metrics interpretation and recommendations

---
**Last Updated**: 2026-02-20
