---
block:
  label: progress_issues
  description: Known issues, research requests, and backlog items
  chars_limit: 4000
  read_only: false
  tier: core
  priority: 2
created: 2026-02-20
modified: 2026-02-20
version: "1.0"
---

# Issues & Backlog

## Current Issues

### 1. Redis Persistence Error - RESOLVED ✅
- **Incident**: Redis RDB snapshot permission denied on /data directory
- **Root Cause**: Container UID (999) couldn't write to host-mounted directory
- **Resolution**: Recreated /data/redis with chmod 777, restarted services
- **Status**: RESOLVED

### 2. Memory Utilization - RAG API High (94%)
- **Finding**: RAG API using 5.61GB / 6GB after LLM initialization
- **Impact**: Limits headroom for concurrent requests
- **Root Cause**: Qwen3-0.6B model + embeddings + context cache
- **Status**: Monitoring - Phase 5 profiling scheduled

### 3. zRAM Optimization Needed
- **Current**: 8GB physical RAM + 12GB zRAM configured
- **Issue**: OOM errors when VS Code + stack running simultaneously
- **Status**: Phase 5 design created, ready for testing
- **Action**: Kernel tuning (vm.swappiness=180), stress testing

### 4. Observable Features - Prometheus Not Available
- **Finding**: Metrics export disabled - missing opentelemetry exporter
- **Impact**: Cannot export metrics to Prometheus/Grafana
- **Status**: Identified for Phase 6 Observable implementation
- **Action**: Replace with VictoriaMetrics (planned)

### 5. Build System Status - AUDITED & IMPROVED
- **Makefile**: 1,952 lines, 133 targets - well organized but large
- **Dockerfiles**: All 7 standardized
- **Status**: Build system working well
- **Research**: Make vs. Taskfile vs. Nix evaluation pending

---

## Active Work Streams

| Stream | Owner | Status | Next Action |
|--------|-------|--------|-------------|
| Research and Resolution | Grok MC | Research phase | Provide research results |
| Vikunja Deployment | OpenCode-GPT-5 mini | Operational | Implement Redis fix |
| Documentation | Cline-Kat | Planning | Implement improvements |
| Stack Alignment | Grok MC | Review | Complete assessment |
| Voice Optimization | Cline-Trinity | Pending | Performance tuning |

---
**Last Updated**: 2026-02-20
