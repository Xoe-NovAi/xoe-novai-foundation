# EXECUTION STRATEGY: Phase 4-5 Transition & Stack Hardening
**Date**: February 12, 2026  
**Status**: Strategic Planning Phase  
**Objective**: Execute complex multi-part request with Phase 4 closure and Phase 5 launch

---

## REQUEST SUMMARY

### Part A: Immediate Issue Resolution
1. **Redis Connection Refused** - Investigate why Redis is giving connection refused (was up, now down)
2. **Chainlit Error Logs** - Inspect what error Chainlit showed at 8001
3. **docker-compose.vikunja.yml** - Why hasn't this been built yet?

### Part B: Build System Analysis & Improvement
1. **Makefile Review** - Is it well-structured? Needs optimization? Size concerns?
2. **All Dockerfiles Review** - Use Dockerfile.base as template, bring all into harmony
3. **Build File Harmony** - Ensure consistency across all Dockerfile + yml files

### Part C: Research Generation for Claude Sonnet
1. **Makefile & Build Tools** - Architecture, optimization strategies, next-gen tooling
2. **Industry-Level Roadmap** - 1-2 year path to compete with Microsoft, LM Studio, Ollama
3. **zRAM Optimization** - Address OOM errors with ML stack memory pressure (12GB swap, 16GB total)

### Part D: Phase 5 Execution
1. **zRAM Optimization** - Implement memory pressure management
2. **Metrics Testing** - Run in terminal (no VS Code), capture real stack memory usage
3. **Performance Baseline** - Document without IDE overhead

### Part E: Documentation & Delivery
1. **Memory Bank Update** - Record Phase 4 closure, Phase 5 findings
2. **Research Reports** - Add sections to Claude Sonnet materials
3. **GitHub Push** - Comprehensive commit with all metadata

---

## EXECUTION PHASES

### PHASE A: INCIDENT INVESTIGATION (30 min)
**Goals**: Restore service health, understand failure points

**Steps**:
1. Check if Redis container is actually running: `podman ps -a | grep redis`
2. Inspect Redis logs: `podman logs xnai_redis`
3. Restart Redis if needed: `podman-compose -f docker-compose.yml restart xnai_redis`
4. Verify connection works: `redis-cli -h 127.0.0.1 -p 6379 -a "changeme123" ping`
5. Check Chainlit logs: `podman logs xnai_chainlit_ui | tail -50`
6. Identify Chainlit error pattern and root cause

**Parallel**: Check if Vikunja build exists or if it's a separate compose file issue

---

### PHASE B: BUILD SYSTEM AUDIT (1 hour)
**Goals**: Holistic understanding of build infrastructure

**Steps**:
1. **Makefile Analysis**:
   - Count lines and target count
   - Identify organization patterns
   - Check for redundancy
   - Benchmark execution time
   - Research: what are modern alternatives (Taskfile, Nix, Bazel)?

2. **Dockerfile Review**:
   - Parallel read all 6 Dockerfiles
   - Identify patterns in Dockerfile.base (latest, most aligned)
   - Check for: cache mounting, multi-stage builds, layer optimization
   - Compare across all files for inconsistencies
   - Note best practices to propagate

3. **Docker-Compose/YAML Review**:
   - Review docker-compose.yml for consistency
   - Check if vikunja has separate compose file (docker-compose.vikunja.yml)
   - Validate all volume mounts, environment variables, resource limits

---

### PHASE C: RESEARCH REQUEST GENERATION (1 hour)
**Goals**: Prepare comprehensive research materials for Claude Sonnet

**Create sections in `_meta/CLAUDE-SONNET-RESEARCH-REQUEST-PHASE-5.md`**:

1. **Makefile & Build Infrastructure Research**:
   - Current state analysis
   - Pain points identified
   - Questions for Claude:
     - Should we migrate to Taskfile/Nix?
     - How to parallelize builds?
     - CI/CD integration strategy?

2. **Industry Competitive Analysis Research**:
   - Stack vs. Microsoft Copilot Stack
   - Stack vs. LM Studio architecture   - Stack vs. Ollama architecture
   - Feature gap analysis
   - 1-2 year product roadmap
   - MVP→Scale→Enterprise progression

3. **zRAM & Memory Optimization Research**:
   - Current situation: 16GB total (1 stick), 12GB zRAM, frequent OOM
   - Questions:
     - zRAM compression ratio optimization for ML workloads?
     - Memory pressure management strategies?
     - Container memory limits vs. kernel swappiness settings?
     - Background service prioritization (what to swap vs. keep resident)?

---

### PHASE D: DOCKERFILE UPDATES (1.5 hours)
**Goals**: Modernize all Dockerfiles with best practices

**Patterns to implement** (from Dockerfile.base):
- Explicit cache cleanup: `apt-get clean && rm -rf /var/lib/apt/lists/*`
- Non-root user earlier in build
- Minimal base image (python:3.12-slim)
- Layer caching optimization
- Health check implementation
- Volume declaration for persistent data

**Process**:
1. Read Dockerfile.base completely (reference)
2. Read all other Dockerfiles (identify gaps)
3. Parallel update all Dockerfiles:
   - Dockerfile (RAG API)
   - Dockerfile.chainlit (Chainlit UI)
   - Dockerfile.crawl (Crawler)
   - Dockerfile.curation_worker (Curation)
   - Dockerfile.docs (MkDocs)
   - Dockerfile.awq (Optional/experimental)
4. Test each rebuild individually
5. Verify docker-compose.yml references match

---

### PHASE E: PHASE 5 LAUNCH - zRAM OPTIMIZATION (2+ hours)
**Goals**: Implement memory pressure management, run metrics

**Steps**:
1. **zRAM Configuration**:
   - Create swapiness tuning guide
   - Document current zRAM status
   - Initial settings: measure OOM frequency
   - Test settings: optimize swap utilization
   - Final settings: validate OOM elimination

2. **Metrics Baseline** (Terminal, no VS Code):
   - Close all VS Code instances
   - Run `btop` to monitor
   - Run stack startup: `podman-compose up -d`
   - Monitor memory during:
     - Initial startup (0-60s)
     - LLM initialization (0-5s)
     - Steady state (1-5 min)
     - Simulate load (15-30 requests)
   - Record: RAM usage, zRAM usage, swap utilization
   - Screenshot/capture output

3. **Stress Test** (Optional):
   - Create minimal load script
   - Monitor until stable
   - Document peak usage

---

### PHASE F: DOCUMENTATION UPDATES (1 hour)
**Goals**: Record all findings, prepare Claude Sonnet materials

**Updates needed**:
1. **memory_bank/progress.md**:
   - Phase 5 start status
   - zRAM findings
   - Metrics results
   - Issues identified (Redis down, Chainlit errors)
   - Next phase entry points

2. **_meta/BUILD-DEPLOYMENT-REPORT-20260212.md**:
   - Add section: "Phase 5 - Incident Investigation Results"
   - Add section: "Phase 5 - Build System Audit Findings"
   - Add section: "Phase 5 - Memory Optimization Baseline"

3. **_meta/CLAUDE-SONNET-RESEARCH-REQUEST-PHASE-5.md**:
   - Complete with all research sections
   - Add zRAM findings from testing
   - Add Makefile analysis
   - Add Dockerfile modernization status
   - Add competitive roadmap questions

---

### PHASE G: GITHUB PUSH (30 min)
**Goals**: Publish all changes with comprehensive metadata

**Commits needed**:
1. **Dockerfile Updates**: "refactor: Modernize all Dockerfiles with cache optimization & multi-stage builds"
2. **Research Addition**: "docs: Phase 5 Research Request - Build Systems & Memory Optimization"
3. **Phase 5 Findings**: "docs: Phase 5 Initial Findings - Incident Response & zRAM Baseline"
4. **Memory Bank Update**: "docs: Phase 5 Progress - Status update & performance baseline"

---

## EXECUTION TIMELINE

| Phase | Est. Time | Status |
|-------|-----------|--------|
| A: Incident Investigation | 30 min | ⏳ Queued |
| B: Build System Audit | 1 hour | ⏳ Queued |
| C: Research Generation | 1 hour | ⏳ Queued |
| D: Dockerfile Updates | 1.5 hours | ⏳ Queued |
| E: Phase 5 Launch | 2+ hours | ⏳ Queued |
| F: Documentation | 1 hour | ⏳ Queued |
| G: GitHub Push | 30 min | ⏳ Queued |
| **TOTAL** | **~7-8 hours** | ⏳ **Queued** |

---

## RESOURCE OPTIMIZATION STRATEGIES

### Parallel Operations:
- Read multiple Dockerfiles simultaneously
- Update multiple Dockerfiles via multi_replace_string_in_file
- Generate research sections while waiting for metric collection
- Watch logs while running tests

### Context Management:
- Use manage_todo_list for tracking 13 subtasks
- Create intermediate summary documents
- Reference previous findings to avoid re-research
- Use semantic_search for quick file location

### Testing Strategy:
- Test Dockerfile changes individually before push
- Run metrics collection without IDE overhead
- Validate each phase before moving to next
- Create checkpoint documents for Phase 5 research

---

## SUCCESS CRITERIA

### Phase A (Incident):
- ✅ Redis connection restored or issue documented
- ✅ Chainlit error identified and logged
- ✅ Vikunja build status identified

### Phase B (Audit):
- ✅ Makefile analysis complete with metrics
- ✅ All Dockerfiles reviewed
- ✅ Inconsistencies documented

### Phase C (Research):
- ✅ Research questions compiled for Claude
- ✅ Analysis frameworks created
- ✅ Competitive positioning assessed

### Phase D (Dockerfiles):
- ✅ All 6 Dockerfiles updated
- ✅ Docker-compose.yml verified
- ✅ Test builds successful

### Phase E (Phase 5):
- ✅ zRAM settings optimized
- ✅ Metrics collected in terminal
- ✅ Baseline established

### Phase F (Documentation):
- ✅ Memory bank updated
- ✅ Research request complete
- ✅ Phase 5 findings recorded

### Phase G (Push):
- ✅ All changes committed
- ✅ Comprehensive messages included
- ✅ GitHub updated

---

## RISK MITIGATION

| Risk | Mitigation |
|------|-----------|
| Redis stays down | Investigate root cause, may indicate deeper issue |
| Chainlit error unclear | Inspect logs in detail, check RAG API connection |
| Makefile too large | Document current state, plan modernization for Phase 6 |
| Dockerfile changes break builds | Test individually, rollback strategy ready |
| OOM errors during Phase 5 | Expected, document occurrences for zRAM tuning |
| Terminal metrics collection fails | Have backup: run tests with minimal services |

---

## Next Action

**START**: Phase A - Incident Investigation
1. Check Redis container status
2. Inspect error logs
3. Identify root causes
4. Fix or document issues

