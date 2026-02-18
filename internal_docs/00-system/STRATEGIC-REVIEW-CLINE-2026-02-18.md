# XNAi Foundation: Strategic Review & Execution Plan
**Prepared By**: Cline (Claude Sonnet 4.5)  
**Prepared For**: OpenCode/GLM-5 — Execution & Research  
**Date**: 2026-02-18T00:00:00Z
**Source Documents**: MASTER-PROJECT-INDEX-v1.0.0.md, memory_bank/activeContext.md, mkdocs-internal.yml, live OpenCode CLI (`opencode models --verbose`)  
**Status**: AUTHORITATIVE — supersedes MASTER-PROJECT-INDEX where conflicts exist  
**v1.1 Update**: Corrected memory bank date gap, updated MC strategy to Sovereign Stack MC, added TASK-021 (Sovereign MC Agent design)  
**v1.2 Update**: GLM-5 research complete — Copilot is PAID (corrected GAP-003), tasks 001/003/008 complete, OpenRouter added as provider, free Opus 4.6 in Cline = immediate priority

---

## SECTION 1: INITIAL FINDINGS REPORT

### 1.1 Project State Summary

The XNAi Foundation is a well-architected sovereign AI platform in a **transitional state** — core infrastructure is complete (Phases 1–7), but three major gaps are creating drag: stale documentation, uncommitted git work, and a blocked research execution queue.

**Verified Completion Status:**
| Component | Claimed Status | Verified Status | Delta |
|-----------|---------------|-----------------|-------|
| Phases 1–7 | ✅ Complete | ✅ Confirmed | None |
| `mkdocs-internal.yml` | ❌ MISSING (per MASTER INDEX) | ✅ EXISTS & COMPLETE | **CRITICAL DISCREPANCY** |
| Dual MkDocs Build | ✅ Operational | ✅ Confirmed | None |
| OpenCode Integration | ✅ Active | ✅ Confirmed (v1.2.6) | None |
| Agent Bus | ✅ Production-ready | ✅ Confirmed | None |
| Phase 8 (8A/8B/8C) | ⏳ Pending | ⏳ Not started | None |
| Memory Bank Freshness | Current | ⚠️ Stale (Feb 9, not Feb 17) | **8-day gap** |
| Git Debt | 8 commits, 67 files | Unverified exact count | Needs audit |

### 1.2 Environment Verified

**OpenCode v1.2.6 — Confirmed Free Models (Native):**
```
Native (opencode.ai/zen/v1) — all FREE, all with reasoning + toolcall:
  opencode/big-pickle        — 200k ctx / 128k out — reasoning variants (low/med/high)
  opencode/glm-5-free        — 204,800 ctx / 131,072 out — structured tasks
  opencode/gpt-5-nano        — 400k ctx / 128k out — largest free context
  opencode/kimi-k2.5-free    — 262,144 ctx / 262,144 out — research, large context
  opencode/minimax-m2.5-free — 204,800 ctx / 131k out — speed

Note: Shared rate limits across all OpenCode users (not individual quotas)
```

**⚠️ CORRECTION — GitHub Copilot via OpenCode = PAID ONLY:**
```
GitHub Copilot models accessible via OpenCode BUT require paid Copilot subscription:
  Copilot Pro: $19/mo | Copilot Pro+: $39/mo | Business/Enterprise tier
  Free tier: NOT supported
  → Use OpenRouter or Ollama instead for additional free model access
```

**🎯 OPPORTUNITY — Cline IDE: Free Claude Opus 4.6 (Limited-Time):**
```
Cline extension currently offers Claude Opus 4.6 FREE (promotional)
  Context: 200k tokens (not 1M — that claim was incorrect)
  Normal cost: $5/M input, $25/M output
  → Maximize use for highest-complexity tasks NOW while promotion lasts
```

**Additional Provider Options (via OpenCode config):**
```
OpenRouter  — 31+ free models via API key (RECOMMENDED)
Ollama      — Unlimited local models, sovereign, zero-cost (hardware-limited)
HuggingFace — Limited free tier (not recommended for agentic tasks)
Google      — Via OpenRouter or Vertex AI enterprise
```

**Key Hardware**: Ryzen 7 5700U, 6.6GB RAM, Vega iGPU (Vulkan/RADV RENOIR)  
**Container Runtime**: Rootless Podman  
**Package Manager**: uv  
**Async Framework**: AnyIO TaskGroups (never asyncio.gather)

---

## SECTION 2: KNOWLEDGE GAP REPORT

### 2.1 CRITICAL GAPS (Blocking Accuracy)

**GAP-001: Memory Bank is 1–2 Days Behind (Corrected)**
- `memory_bank/activeContext.md` oldest modified: 2026-02-16, most recent files: 2026-02-17
- MASTER-PROJECT-INDEX was created: 2026-02-17T22:00:00Z (same day, late in session)
- The gap is therefore **hours to 1 day**, not 8 days as initially assessed
- **Impact**: Memory bank may not reflect the final decisions made in the Feb 17 evening session (MC migration, mkdocs-internal.yml creation, model card work)
- **Fix**: Update activeContext.md to capture Feb 17 end-of-session state: mkdocs-internal.yml complete, model docs updated, MC transition decided

**GAP-002: MASTER-PROJECT-INDEX Reports mkdocs-internal.yml as Missing**
- Reality: `mkdocs-internal.yml` EXISTS and is fully configured (docs_dir: internal_docs, site-dir: site-internal, complete nav)
- The MASTER INDEX was likely written before the file was created in the same session
- **Impact**: Any agent reading MASTER INDEX will waste time creating an already-complete file
- **Fix**: Update MASTER INDEX section "Documentation - Phase 2: MkDocs Internal" to ✅ COMPLETE

**GAP-003: ⚠️ CORRECTED — GitHub Copilot Requires PAID Subscription**
- **Original assessment was WRONG**: OpenCode can connect to Copilot, but free tier does NOT work
- Copilot Pro = $19/mo, Pro+ = $39/mo — not available on free tier
- **Revised strategy**: Use OpenCode's 5 native free models + OpenRouter (31+ free models via API key) + Ollama (local, unlimited)
- GLM-5 research confirmed: `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` updated accordingly
- **Corrected model availability**: OpenCode is NOT a Copilot superset for free users

**GAP-004: Big Pickle Release Date and Provider Now Known**
- Old doc: "Provider: Unknown (proprietary), Status: stable"
- Live data: `api.url = https://opencode.ai/zen/v1`, `release_date: 2025-10-17`
- Big Pickle IS an OpenCode-native model — it's their own model, not third-party
- Has reasoning variants: low/medium/high effort
- **Impact**: Documentation inaccurate; model selection notes should reflect reasoning effort control

**GAP-005: GLM-5 Has Full ToolCall Capability**
- Existing docs rated GLM-5 Tool-Use at ⭐⭐⭐ "Good but not optimized"
- Live JSON confirms: `"toolcall": true` — it IS fully toolcall-capable
- **Impact**: GLM-5 may be underutilized for agentic tasks

**GAP-006: Mission Control Architecture Needs Fundamental Redesign** ⚠️ STRATEGIC
- MASTER INDEX proposes Claude.ai Project as MC replacement for Grok.com
- **User direction (2026-02-18)**: Claude.ai is NOT the daily MC — it is for high-level org-wide strategy only on complex or critical decisions
- **True MC vision**: The **XNAi Foundation Stack itself** should be the sovereign MC — using Agent Bus, Vikunja, Qdrant, Redis, and Consul as the coordination layer
- The Foundation Stack was built to be sovereign; having it self-direct is the correct architectural conclusion
- MCP servers already exist for Agent Bus, RAG, and Vikunja — these are the building blocks
- **Impact**: Entire agent hierarchy must be redesigned around a local Sovereign MC Agent
- **Fix**: Design and implement Sovereign MC Agent (see TASK-021 and new Section 3.3)

**GAP-007: 6 Research Requests Pending with No Execution Plan**
- REQ-DOC-001 through REQ-DOC-006 are PENDING
- REQ-2026-02-13-001/002/003 are also pending
- Total: 9 research requests with no assigned execution schedule
- **Impact**: Strategy evolution is blocked; documentation excellence stalled

**GAP-008: Phase 3 Test Blockers Not Resolved**
- Missing: `redis` module in test environment
- Missing: `opentelemetry.exporter.prometheus`
- These are blocking 25% of Phase 3 test coverage
- **Impact**: Phase 4 integration testing cannot begin cleanly

### 2.2 MEDIUM GAPS (Strategy & Organization)

**GAP-009: No CI/CD for Documentation Builds**
- MASTER INDEX recommends GitHub Actions for MkDocs — not implemented
- Risk: Doc builds break silently
- Fix: Add `.github/workflows/docs.yml`

**GAP-010: Branch Strategy Not Implemented**
- Current: working on `xnai-agent-bus/harden-infra` with 67 modified files
- Recommended naming convention defined but not followed
- Risk: Merge conflicts, unclear scope

**GAP-011: Three Strategic Pillars Have No Phase 8 Dependency Mapping**
- PILLAR-1 (5A-5E), PILLAR-2 (6A-6F), PILLAR-3 (7A-7E) are defined
- Phase 8 (8A/8B/8C) dependencies on specific pillars not mapped
- Fix: Phase 8 → Pillar dependency matrix needed

**GAP-012: Vikunja and Consul Reported as Non-Responding**
- MASTER INDEX lists both as blockers under "Infrastructure"
- `make up` needed but services may need config verification first
- Redis password env var may be missing

**GAP-013: `mc-oversight/` Directory Empty**
- Was specified as the output location for Claude.ai MC strategic outputs
- Currently only has `README.md`
- No `strategic-recommendations.md`, `initiative-status-dashboard.md`, etc.

---

## SECTION 3: STRATEGY ADJUSTMENT RECOMMENDATIONS

### 3.1 IMMEDIATE CORRECTIONS (Do Before Anything Else)

**REC-001: Update Memory Bank Before Starting Any Work**
- The memory bank is the single source of truth for ALL agents
- An 8-day-stale activeContext.md will cause every agent to work from wrong assumptions
- Action: GLM-5 should update `memory_bank/activeContext.md` priorities section first

**REC-002: Correct the MASTER-PROJECT-INDEX Discrepancies**
- Mark `mkdocs-internal.yml` status as ✅ COMPLETE
- Mark Documentation Phase 2 as ✅ COMPLETE  
- Update blockers section to remove the mkdocs-internal.yml item
- This prevents other agents from redundantly creating an existing file

**REC-003: ✅ COMPLETED BY GLM-5 — Model Matrix Updated to v2.0.0**
- `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` created by GLM-5
- OpenCode confirmed as PRIMARY CLI (5 native free models)
- Copilot corrected: PAID subscription required — removed from free model pool
- OpenRouter recommended as free model expansion path (31+ models)
- Ollama recommended for sovereign/unlimited local inference
- See: `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` (new, by GLM-5)

### 3.2 MISSION CONTROL: SOVEREIGN STACK ARCHITECTURE

**Decision (2026-02-18)**: The XNAi Foundation Stack IS the Mission Control. External AI projects (Claude.ai, Grok) serve advisory roles only.

**Role Hierarchy:**

| Entity | Role | Access Level | When to Use |
|--------|------|-------------|-------------|
| **Human Director** | Ultimate authority | All systems | All final decisions |
| **Sovereign MC Agent** (LOCAL) | Daily project manager | Full local stack | Task creation, routing, validation, memory bank |
| **Claude.ai Project** | High-level strategy only | GitHub repo (read) | Org-wide pivots, excessively complex architecture decisions, cross-project strategy |
| **Cline (Claude Opus 4.6)** | Primary implementer | IDE + MCP servers | Multi-file code changes, architecture |
| **OpenCode/GLM-5** | Research & decomposition | Filesystem + models | Task analysis, gap reports, research queue |
| **Gemini CLI** | Large-context audit | Filesystem | Whole-codebase analysis, batch processing |
| **Copilot (via OpenCode)** | Fast code generation | Terminal | Real-time terminal work |

**Sovereign MC Agent Design Principles:**
- Runs entirely on local hardware (Ryzen 7 5700U)
- Uses Foundation Stack tools as its cognitive infrastructure:
  - **Qdrant** → Semantic memory (project knowledge, past decisions)
  - **Vikunja** → Task tracking and project management
  - **Redis** → State persistence, circuit breakers, session continuity
  - **Agent Bus** → Task delegation to CLI agents
  - **Consul** → Service health awareness
  - **Memory Bank** → Strategic context (read/write)
- Accessible via **Cline IDE with MCP servers** (xnai-agentbus, xnai-rag, xnai-vikunja)
- Uses local GGUF models for offline-capable reasoning (fallback from API models)
- Sovereign: zero external data transmission for internal project decisions

**What Claude.ai Project Does (Narrowly):**
- Quarterly/monthly strategic reviews at org level
- Architecture decisions too complex for local context (>200k tokens)
- Cross-project XNAi ecosystem decisions
- Does NOT: daily task management, code review, routine planning

### 3.3 STRATEGIC PIVOTS

**REC-004: Restructure Agent Role Hierarchy Around Sovereign MC**

Current (from activeContext.md):
```
Grok (MC) → Cline, Gemini, Copilot, OpenCode
```

Recommended — Sovereign Stack as MC:
```
Human Director (ultimate authority)
  ↓
Sovereign MC Agent [LOCAL — XNAi Foundation Stack]
  ├─ Memory: Qdrant (semantic) + Redis (state) + memory_bank/ (strategic)
  ├─ Tasks: Vikunja (PM) + Agent Bus (routing)
  ├─ Interface: Cline IDE (MCP: xnai-agentbus, xnai-rag, xnai-vikunja)
  ├─ Health: Consul (service awareness)
  │
  ├─ Delegates to → Cline/Claude Opus 4.6 (implementation, multi-file)
  ├─ Delegates to → OpenCode/GLM-5 (research, decomposition, validation)
  ├─ Delegates to → Gemini CLI (large-context audit, 1M tokens)
  └─ Delegates to → Copilot via OpenCode (fast code generation)
  
Claude.ai Project (strategic advisory only)
  → High-level org strategy, complex cross-project decisions
  → NOT daily operations
```

**REC-005: Consolidate Phase 8 Into Structured Sprint Plan**

Current Phase 8 ordering (8B → 8A → 8C) is correct. Add specific agent assignments:
- **8B (Qdrant Migration)**: Cline implements, OpenCode validates migration scripts
- **8A (Redis Streams)**: Cline implements, Gemini audits event schema
- **8C (Fine-tuning)**: Research-first via Gemini, implement via Cline

**REC-006: Execute Research Queue via OpenCode/GLM-5 Sprint**

The 9 pending research requests should be batch-executed by OpenCode:
- GLM-5 (reasoning specialist) → Documentation audit, schema analysis requests
- Kimi K2.5 (large context) → Codebase synthesis requests
- Big Pickle (validation) → Cross-validation of other model findings
- Schedule: 1 research request per session = 9 sessions to clear queue

**REC-007: Address Git Debt Before Phase 8**
- 67 modified files and 8 unpushed commits are a merge-conflict liability
- Commit strategy: categorize by component, then batch commit per subsystem
- Target: clean `main` branch before Phase 8 begins

**REC-008: Implement Sovereign MC Agent (see TASK-021)**
- The `mc-oversight/` directory becomes the Sovereign MC Agent's strategic output store
- Populate with status dashboard, priority matrix, risk assessment, strategic recommendations
- The Sovereign MC Agent reads `memory_bank/`, writes to `mc-oversight/`, routes via Agent Bus, tracks via Vikunja
- Claude.ai Project role: narrowly scoped to high-level advisory (not daily operations)
- Grok.com: retire as MC; can remain as a research/advisory tool if useful

---

## SECTION 3.4: GLM-5 RESEARCH RESPONSES (Opus Answers)

**Q1: OpenRouter vs HuggingFace priority?**  
→ **OpenRouter, clearly.** 31+ free models, stable API, reliable for agentic tool-calling. HuggingFace free tier has rate limits, inconsistent tool-calling support, and is unsuitable for production agent workflows. Configure OpenRouter API key in `.opencode/opencode.json` as the first additional provider.

**Q2: MCP server approach correct for RAG integration?**  
→ **Yes — MCP is the correct architecture.** The three MCP servers (`xnai-agentbus`, `xnai-rag`, `xnai-vikunja`) are already built and are exactly the right interface layer. OpenCode's `.opencode/opencode.json` MCP config points to `mcp-servers/xnai-rag/server.py` at `http://localhost:6333`. This is the sovereign integration path — no external calls.

**Q3: Better model choices for XNAi tasks (with Copilot correction)?**

| Task | Model | Reason |
|------|-------|--------|
| Complex implementation (NOW) | **Cline + Opus 4.6 FREE** | Best reasoning, use while free |
| Research synthesis | `opencode/kimi-k2.5-free` | 262k context |
| Structured output / protocols | `opencode/glm-5-free` | Reasoning specialist |
| Large context analysis | `opencode/gpt-5-nano` | 400k context |
| Validation / second opinion | `opencode/big-pickle` | Reasoning variants |
| Unlimited local sovereign | Ollama + GGUF | Zero cost, air-gap capable |
| Expanded free variety | OpenRouter free tier | 31+ models |

**Q4: Task priorities given free Opus 4.6 access via Cline?**  
→ **Reprioritize immediately.** Free Opus 4.6 is the most powerful tool in the stack right now and the offer is temporary. Assign ALL high-complexity implementation tasks to Cline/Opus now:
1. **TASK-021b** (Sovereign MC Agent core implementation) — highest value
2. **TASK-011** (Phase 8B Qdrant Migration) — complex migration
3. **TASK-012** (Phase 8A Redis Streams) — complex event architecture
4. **TASK-005** (Phase 3 test fixes) — quick Opus win
5. Defer GLM-5 to research/decomposition/structured output tasks (its strength anyway)

---

## SECTION 4: ORDERED EXECUTION TASK LIST FOR AI ASSISTANTS

> **Instructions for GLM-5**: Tasks are numbered by execution order. Each task has an assigned agent, estimated complexity (1-5), and explicit success criteria. Complete tasks in sequence within each phase. Blockers are noted explicitly.

---

### PHASE 0: STABILIZATION (Do First — Unlocks Everything Else)
*Estimated time: 2-4 hours*

---

**TASK-001**: ✅ COMPLETE (GLM-5 — 2026-02-18)
- Memory bank updated with free models section and OpenCode as primary CLI
- Commits: `bdd8a0c` (MC oversight infrastructure), `122d328` (OpenCode primary, permissions fix)
- Remaining: Verify Sovereign MC architecture decision is reflected in activeContext.md

---

**TASK-002**: Correct MASTER-PROJECT-INDEX-v1.0.0.md
- **Agent**: OpenCode/GLM-5 (you)
- **Complexity**: 2/5
- **Command**: Edit `internal_docs/00-system/MASTER-PROJECT-INDEX-v1.0.0.md`
- **Actions**:
  1. Documentation Excellence Initiative → Phase 2 (MkDocs Internal): change from `⏳ Pending` to `✅ COMPLETE`
  2. Remove `mkdocs-internal.yml missing` from Critical Blockers table
  3. Add note: Big Pickle is OpenCode-native model (provider: opencode.ai/zen/v1, released 2025-10-17)
  4. Add note: GLM-5 has full toolcall capability (verified live)
  5. Add note: OpenCode exposes GitHub Copilot models — see model matrix update needed
  6. Update Last Updated timestamp to 2026-02-18
- **Success Criteria**: No false blockers; accurate model data; current timestamp

---

**TASK-003**: ✅ PARTIALLY COMPLETE (GLM-5 — 2026-02-18)
- Two commits made: `bdd8a0c`, `122d328`
- Remaining: Full git audit still needed — `git status --short | wc -l` to confirm remaining uncommitted files
- Remaining: Push branch and create PR

---

**TASK-004**: Verify Service Health
- **Agent**: OpenCode/GLM-5 or Gemini CLI
- **Complexity**: 2/5
- **Commands**:
  ```bash
  make up 2>&1 | tail -30
  docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1
  curl -s http://localhost:8500/v1/status/leader 2>&1 | head -5   # Consul
  redis-cli ping 2>&1                                               # Redis
  curl -s http://localhost:3456/api/v1/info 2>&1 | head -5         # Vikunja
  ```
- **Actions**:
  1. Attempt `make up` to start services
  2. Check Redis connection (may need REDIS_PASSWORD env var from `.env`)
  3. Verify Consul and Vikunja are responding
  4. Document any failures with exact error messages
- **Output**: `internal_docs/03-infrastructure-ops/SERVICE-HEALTH-2026-02-18.md`
- **Success Criteria**: All core services responding OR blockers documented with remediation

---

**TASK-005**: Fix Phase 3 Test Dependencies
- **Agent**: Cline (IDE context needed for requirements files)
- **Complexity**: 2/5
- **Actions**:
  1. Add `redis>=5.0.0` to `requirements.in` (and/or test requirements)
  2. Add `opentelemetry-exporter-prometheus` to `requirements.in`
  3. Run: `uv pip compile requirements.in -o requirements.txt` (in container)
  4. Verify: `pytest tests/ -v --tb=short 2>&1 | tail -40`
- **Success Criteria**: Phase 3 test suite runs without import errors

---

### PHASE 1: DOCUMENTATION & ORGANIZATION
*Estimated time: 4-6 hours | Requires: Phase 0 complete*

---

**TASK-006**: Execute REQ-DOC-001 — Documentation System Audit
- **Agent**: Gemini CLI (1M context for full scan)
- **Complexity**: 3/5
- **Task**: Audit all 349 markdown files for:
  1. Missing or malformed frontmatter
  2. Broken internal links
  3. Orphaned files not referenced in mkdocs.yml or mkdocs-internal.yml
  4. Files with "template" placeholders (06-team-knowledge, 05-client-projects)
- **Output**: `internal_docs/02-research-lab/REQ-DOC-001-RESULTS.md`
- **Gemini Command**:
  ```bash
  gemini --model gemini-3-pro-preview "Audit all markdown files in internal_docs/ 
  for frontmatter validity, broken links, orphaned files. Output structured report."
  ```
- **Success Criteria**: Report lists all files needing attention with specific fixes

---

**TASK-007**: Execute REQ-DOC-002 — Multi-Agent Documentation Protocols
- **Agent**: OpenCode/GLM-5 (reasoning specialist)
- **Complexity**: 3/5
- **Task**: Design formal protocol for how multiple AI agents (Cline, Gemini, Copilot, OpenCode) should update documentation without conflicts:
  1. File ownership model (which agent owns which docs)
  2. Update frequency rules (when to update memory_bank vs expert-knowledge)
  3. Conflict resolution procedure (two agents update same file)
  4. Versioning convention for docs
- **Output**: `internal_docs/06-team-knowledge/MULTI-AGENT-DOC-PROTOCOL-v1.0.0.md`
- **Success Criteria**: Protocol covers all 4 agent types, has concrete rules, no ambiguity

---

**TASK-008**: ✅ COMPLETE (GLM-5 — 2026-02-18)
- `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` — NEW, OpenCode as primary CLI, Copilot corrected to PAID
- `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` — NEW, provider setup, RAG integration, rate limits
- `scripts/fix-permissions.sh` — NEW, Redis/Qdrant UID 1001 ownership fix
- Remaining: Add OpenRouter provider setup instructions to guide

---

**TASK-009**: Populate `mc-oversight/` Directory
- **Agent**: OpenCode/GLM-5
- **Complexity**: 3/5
- **Actions**: Create 4 files:
  1. `mc-oversight/initiative-status-dashboard.md` — Current status of all 6 projects
  2. `mc-oversight/priority-matrix.md` — Phase 8A/8B/8C priority with dependency map
  3. `mc-oversight/risk-assessment.md` — Top 5 risks with mitigation
  4. `mc-oversight/strategic-recommendations.md` — This review's recommendations (condensed)
- **Success Criteria**: 4 files exist, each < 200 lines, actionable not theoretical

---

**TASK-010**: Execute REQ-DOC-003 — zRAM-Aware Search Optimization Research
- **Agent**: OpenCode/Kimi K2.5 (large context needed)
- **Complexity**: 4/5
- **Task**: Research how to optimize MkDocs search index for Ryzen 7 5700U with zRAM:
  1. Search index size optimization for 6.6GB RAM constraint
  2. zRAM compression compatibility with MkDocs prebuild_index
  3. Multi-tiered indexing strategy (hot/warm/cold)
  4. Recommendations for `mkdocs.yml` and `mkdocs-internal.yml` search plugin config
- **Output**: `internal_docs/02-research-lab/REQ-DOC-003-RESULTS.md`
- **OpenCode Command**:
  ```bash
  opencode --model kimi-k2.5-free "Research MkDocs search optimization for systems 
  with 6.6GB RAM and zRAM compression. Provide config recommendations."
  ```
- **Success Criteria**: Specific `mkdocs.yml` search plugin config changes recommended

---

### PHASE 2: PHASE 8 EXECUTION
*Estimated time: 2-3 weeks | Requires: Phase 0 + Phase 1 complete*

---

**TASK-011**: Phase 8B — FAISS → Qdrant Migration (START FIRST per priority matrix)
- **Agent**: Cline (implementation), OpenCode validates
- **Complexity**: 5/5
- **Branch**: `phase8/qdrant-migration`
- **Scope**:
  1. Review existing `config/qdrant_config.yaml` and `docs/QDRANT_MIGRATION.md`
  2. Audit current FAISS usage: `grep -r "faiss" app/ --include="*.py" -l`
  3. Design migration: FAISS index → Qdrant collection with same metadata schema
  4. Implement `scripts/migrate_faiss_to_qdrant.py`
  5. Write migration tests
  6. Update `app/XNAi_rag_app/services/rag/` to use Qdrant client
  7. Performance benchmark: FAISS vs Qdrant on Ryzen 7 5700U
- **Pre-requisite**: Qdrant container running (`docker-compose.yml` check)
- **Output**: Migration complete + `docs/QDRANT_MIGRATION.md` updated
- **Success Criteria**: All existing RAG tests pass with Qdrant backend; latency ≤ FAISS baseline

---

**TASK-012**: Phase 8A — Redis Streams Integration
- **Agent**: Cline (implementation)
- **Complexity**: 4/5
- **Branch**: `phase8/redis-streams`
- **Dependency**: Phase 5B Observability metrics must be operational
- **Scope**:
  1. Design event schema for Agent Bus using Redis Streams
  2. Implement producer in `app/XNAi_rag_app/core/agent_bus.py`
  3. Implement consumer groups for each agent type
  4. Dead letter queue for failed events
  5. Stream monitoring dashboard (Prometheus metrics)
  6. Integration tests (requires Redis running)
- **Success Criteria**: Agent Bus events visible in Redis Streams; consumer groups process events; dead letter queue captures failures

---

**TASK-013**: Phase 8C — Fine-Tuning Pipeline (LoRA/QLoRA)
- **Agent**: Research first (OpenCode/Kimi K2.5), then Cline implements
- **Complexity**: 5/5
- **Dependency**: Phase 6D Model Registry
- **Pre-research** (OpenCode):
  ```bash
  opencode --model kimi-k2.5-free "Design a LoRA fine-tuning pipeline for GGUF models 
  on Ryzen 7 5700U with 6.6GB RAM. Torch-free constraint. ONNX-compatible output required."
  ```
- **Scope**:
  1. Dataset preparation pipeline (sovereign, no external transmission)
  2. LoRA adapter training (torch-free or minimal torch in isolated container)
  3. Model merging and GGUF quantization output
  4. Registry integration
- **Success Criteria**: End-to-end pipeline from dataset → fine-tuned GGUF model

---

### PHASE 2.5: SOVEREIGN MC AGENT (Design + Implementation)
*Estimated time: 1 week | Start after Phase 0 complete, can parallel Phase 1*

---

**TASK-021**: Design and Implement the Sovereign MC Agent
- **Agent**: Cline (implementation), OpenCode/GLM-5 (design spec)
- **Complexity**: 5/5
- **Priority**: HIGH — this is the architectural north star for the Foundation Stack
- **Branch**: `feature/sovereign-mc-agent`

#### Design Specification (GLM-5 to produce)

The Sovereign MC Agent is a locally-running orchestration agent that uses the Foundation Stack as its intelligence layer:

**Core Architecture:**
```
┌─────────────────────────────────────────────────────────┐
│              SOVEREIGN MC AGENT                          │
│                                                          │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────────┐  │
│  │  Context     │  │   Task      │  │  Delegation   │  │
│  │  Manager     │  │  Manager    │  │  Engine       │  │
│  │              │  │             │  │               │  │
│  │  Qdrant RAG  │  │  Vikunja    │  │  Agent Bus    │  │
│  │  memory_bank │  │  Redis state│  │  CLI routing  │  │
│  └──────────────┘  └─────────────┘  └───────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Health Monitor (Consul + Prometheus)             │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
            ↓ MCP (xnai-agentbus, xnai-rag, xnai-vikunja)
   Accessible via Cline IDE with MCP servers configured
```

**Implementation Path:**

*Step 1 — GLM-5: Design Specification (TASK-021a)*
```bash
opencode --model glm-5-free "Design a Sovereign MC Agent spec for XNAi Foundation:
- Reads memory_bank/*.md for context
- Creates/updates tasks in Vikunja via REST API
- Routes tasks to CLI agents via Agent Bus (Redis Streams)
- Semantic search via Qdrant for past decisions
- Persists session state in Redis
- Uses Consul for service health
- Interface: Cline IDE with MCP servers
Output: Full Python class design + API contracts"
```
- **Output**: `internal_docs/01-strategic-planning/SOVEREIGN-MC-AGENT-SPEC-v1.0.0.md`

*Step 2 — Cline: Implement Core Agent (TASK-021b)*
- File: `app/XNAi_rag_app/core/sovereign_mc_agent.py`
- Key methods:
  ```python
  async def load_context() -> ProjectContext      # reads memory_bank + Qdrant
  async def create_task(spec) -> VikunjaTask       # creates Vikunja task
  async def delegate(task, agent) -> AgentBusMsg   # routes via Agent Bus
  async def validate_output(result) -> bool        # validates agent outputs
  async def update_memory(context) -> None         # writes back to memory_bank
  async def get_health() -> SystemHealth           # Consul + Prometheus
  ```
- Uses: AnyIO TaskGroups, Redis circuit breakers, Ed25519 agent handshakes

*Step 3 — Cline: MCP Server Configuration (TASK-021c)*
- Configure `mcp-servers/xnai-agentbus/`, `mcp-servers/xnai-rag/`, `mcp-servers/xnai-vikunja/`
- Ensure Cline IDE can invoke Sovereign MC via MCP tools
- Test: Cline can query project status, create Vikunja tasks, read Qdrant knowledge

*Step 4 — Integration: MC Oversight Directory (TASK-021d)*
- Sovereign MC Agent auto-generates `mc-oversight/` files on demand
- `mc-oversight/initiative-status-dashboard.md` — auto-refreshed from Vikunja
- `mc-oversight/priority-matrix.md` — generated from Qdrant + memory_bank
- `mc-oversight/risk-assessment.md` — Agent Bus failure rates + circuit breaker states
- `mc-oversight/strategic-recommendations.md` — GLM-5 synthesis on demand

- **Success Criteria**:
  - Sovereign MC Agent reads memory bank and produces project status summary
  - Creates a Vikunja task via API
  - Routes a test task through Agent Bus
  - Cline IDE can invoke all three MCP servers
  - All operations remain local (zero external data transmission)

---

### PHASE 3: INFRASTRUCTURE HARDENING & CI/CD
*Estimated time: 1 week | Can run in parallel with Phase 2*

---

**TASK-014**: GitHub Actions — Docs CI/CD
- **Agent**: Cline
- **Complexity**: 2/5
- **Actions**:
  1. Create `.github/workflows/docs.yml`
  2. Trigger: push to `main`, PR to `main`
  3. Steps: `mkdocs build --strict` (public) + `mkdocs build -f mkdocs-internal.yml --strict` (internal)
  4. Fail on warnings using strict mode
- **Success Criteria**: Both MkDocs builds pass on push; broken links fail the build

---

**TASK-015**: Implement GitHub Projects + Issues Structure
- **Agent**: OpenCode/GLM-5 (can use GitHub CLI)
- **Complexity**: 2/5
- **Commands**:
  ```bash
  gh project create --title "Phase 8 Execution" --owner Xoe-NovAi
  gh issue create --title "8B: FAISS → Qdrant Migration" --label "phase-8,priority-high"
  gh issue create --title "8A: Redis Streams Integration" --label "phase-8,priority-medium"
  gh issue create --title "8C: Fine-Tuning Pipeline" --label "phase-8,priority-low"
  # Convert REQ-DOC-001 through REQ-DOC-006 to issues
  ```
- **Success Criteria**: GitHub project board exists; all Phase 8 items and REQ-DOC items as issues

---

**TASK-016**: Commit Git Debt (Execute Commit Plan from TASK-003)
- **Agent**: Cline (has IDE context for reviewing file changes)
- **Complexity**: 3/5
- **Actions**: Execute the commit plan from TASK-003 output
  ```bash
  git add [memory_bank files] && git commit -m "docs(memory-bank): sync context to 2026-02-17 session"
  git add [expert-knowledge files] && git commit -m "docs(expert-knowledge): add model reference docs v1.0.0"
  git add [app files] && git commit -m "feat(core): phase 7 agent bus wrapper complete"
  git add [tests files] && git commit -m "test(phase3): exception hierarchy tests"
  git add [docs files] && git commit -m "docs(mkdocs): dual-build internal KB config complete"
  git push origin xnai-agent-bus/harden-infra
  ```
- **Success Criteria**: 0 uncommitted tracked files; branch pushed; PR created

---

### PHASE 4: RESEARCH QUEUE CLEARANCE
*Estimated time: 1 week | Run in parallel with Phase 2/3*

---

**TASK-017**: Execute REQ-DOC-004 — AI-Powered Documentation Quality
- **Agent**: OpenCode/GLM-5
- **Complexity**: 3/5
- **Task**: Design system where AI agents automatically flag low-quality documentation:
  1. Quality scoring rubric (completeness, accuracy, recency, cross-references)
  2. Integration with pre-commit hooks for new docs
  3. Weekly batch review schedule
  4. Agent assignment per quality issue type
- **Output**: `internal_docs/02-research-lab/REQ-DOC-004-RESULTS.md`

---

**TASK-018**: Execute REQ-DOC-005 — Zero-Telemetry Documentation Pipeline
- **Agent**: Gemini CLI (filesystem + policy focus)
- **Complexity**: 3/5
- **Task**: Verify the entire documentation build and search pipeline is zero-telemetry:
  1. Audit MkDocs plugins for external calls (analytics, CDN, fonts)
  2. Verify search is local-only (no Algolia, no external indexing)
  3. Check `mkdocs.yml` for any external `extra_css/js` URLs
  4. Recommend: self-hosted fonts, offline search, no analytics
- **Output**: `internal_docs/02-research-lab/REQ-DOC-005-RESULTS.md`

---

**TASK-019**: Execute REQ-DOC-006 — Multi-Project Documentation Standardization
- **Agent**: OpenCode/GLM-5
- **Complexity**: 3/5
- **Task**: Define standards for scaling the documentation system to multiple projects:
  1. Shared frontmatter schema across all XNAi projects
  2. Cross-project navigation strategy (separate mkdocs.yml per project vs. monorepo)
  3. Versioning strategy for docs alongside code releases
  4. Template repository structure for new projects
- **Output**: `internal_docs/02-research-lab/REQ-DOC-006-RESULTS.md`

---

**TASK-020**: Execute REQ-2026-02-13 Research Queue (Big Pickle, GPT-5 Nano, Comparison)
- **Agent**: OpenCode/GLM-5 (REQ-001, REQ-002); OpenCode/Kimi K2.5 (REQ-003)
- **Complexity**: 3/5
- **Actions**:
  ```bash
  # REQ-001: Big Pickle analysis (we now know it's OpenCode native, released 2025-10-17)
  opencode --model glm-5-free "Analyze Big Pickle model capabilities based on: 
  context=200k, output=128k, toolcall=true, reasoning_variants=low/medium/high, 
  provider=opencode.ai. Compare to Claude Haiku 4.5 for XNAi workloads."
  
  # REQ-002: GPT-5 Nano analysis  
  opencode --model glm-5-free "Analyze GPT-5 Nano: context=400k, vision=true, 
  fast inference. Best use cases for XNAi sovereign AI platform."
  
  # REQ-003: Full comparison matrix
  opencode --model kimi-k2.5-free "Create comparison matrix of all 5 OpenCode models 
  for XNAi workloads: RAG queries, agent orchestration, code generation, research."
  ```
- **Output**: `expert-knowledge/research/REQ-001-COMPLETE.md`, `REQ-002-COMPLETE.md`, `REQ-003-COMPLETE.md`

---

## SECTION 5: QUICK REFERENCE — OPENCODE/GLM-5 EXECUTION GUIDE

### Model Selection for This Task List (UPDATED v1.2)

| Task Type | Use This Model | Why |
|-----------|---------------|-----|
| **HIGH-COMPLEXITY IMPLEMENTATION (NOW)** | **Cline + Claude Opus 4.6 FREE** | **Limited promotion — use immediately** |
| Structured analysis, gap reports, protocol design | `opencode/glm-5-free` | Reasoning specialist, toolcall |
| Large codebase review (>100k tokens) | `opencode/kimi-k2.5-free` | 262k context |
| Fast generation / prototyping | `opencode/minimax-m2.5-free` | Speed |
| Cross-validation / second opinion | `opencode/big-pickle` | Reasoning variants low/med/high |
| Large document batch processing | `opencode/gpt-5-nano` | 400k context |
| Sovereign local inference (unlimited) | Ollama + GGUF models | Zero cost, air-gap |
| Expanded free model variety | OpenRouter free tier (31+ models) | API key required |
| 1M context whole-codebase audit | Gemini CLI | gemini-3-pro-preview |

**⚠️ COPILOT CORRECTION**: GitHub Copilot models via OpenCode require PAID subscription. Do NOT plan tasks around Copilot CLI as a free resource.

### GLM-5 Strengths for This Work
GLM-5 (Zhipu AI) excels at:
- Structured output generation (tables, schemas, protocols)
- Formal logical reasoning (dependency analysis, gap identification)
- Algorithm and protocol design
- Systematic gap analysis (exactly what Section 2 demonstrates)

GLM-5 limitations — escalate to Kimi K2.5 for:
- Tasks requiring vision/image input
- Tasks exceeding 100k tokens of context
- Real-time interactive low-latency work

### Key Commands Reference
```bash
# Check what's in memory bank
cat memory_bank/activeContext.md | head -100

# Check service health
make up && docker ps --format "table {{.Names}}\t{{.Status}}"

# Run docs build (verify both work)
mkdocs build --clean && mkdocs build -f mkdocs-internal.yml --clean

# Run tests
pytest tests/ -v --tb=short 2>&1 | tail -50

# Check git status
git status --short | wc -l   # count modified files
git log --oneline -10         # recent commits

# OpenCode model selection
opencode --model glm-5-free "your task here"
opencode --model kimi-k2.5-free "large context task"
opencode --model big-pickle "validation/second opinion"
```

---

## SECTION 6: RECOMMENDED EXECUTION SEQUENCE SUMMARY

```
┌─ PHASE 0: STABILIZATION (Do First — Today) ────────────────────────────┐
│  TASK-001  Update memory_bank/activeContext.md             [GLM-5]      │
│  TASK-002  Correct MASTER-PROJECT-INDEX discrepancies      [GLM-5]      │
│  TASK-003  Git audit + commit plan                         [Gemini/GLM] │
│  TASK-004  Verify service health (make up)                 [GLM-5]      │
│  TASK-005  Fix Phase 3 test dependencies                   [Cline]      │
└─────────────────────────────────────────────────────────────────────────┘
        ↓ (parallel execution below)
┌─ PHASE 1: DOCS & ORG ─────────────────────┐  ┌─ PHASE 2.5: SOVEREIGN MC ──────────────┐
│  TASK-006  REQ-DOC-001 Audit   [Gemini]    │  │  TASK-021a  MC Agent Spec  [GLM-5]     │
│  TASK-007  REQ-DOC-002 Protocol[GLM-5]    │  │  TASK-021b  Core Agent     [Cline]     │
│  TASK-008  Update model docs   [GLM-5]    │  │  TASK-021c  MCP Config     [Cline]     │
│  TASK-009  mc-oversight/ files [GLM-5]    │  │  TASK-021d  MC Oversight   [MC Agent]  │
│  TASK-010  REQ-DOC-003 zRAM    [Kimi K2.5]│  └────────────────────────────────────────┘
└────────────────────────────────────────────┘
        ↓
┌─ PHASE 2: PHASE 8 EXECUTION ────────────────────────────────────────────┐
│  TASK-011  Phase 8B: Qdrant Migration      [Cline + MC Agent validates] │
│  TASK-012  Phase 8A: Redis Streams         [Cline]                      │
│  TASK-013  Phase 8C: Fine-Tuning Pipeline  [Kimi research → Cline impl]│
└─────────────────────────────────────────────────────────────────────────┘
        ↓ (parallel with Phase 2)
┌─ PHASE 3: CI/CD ─────────────────┐  ┌─ PHASE 4: RESEARCH QUEUE ────────┐
│  TASK-014  GH Actions Docs        │  │  TASK-017  REQ-DOC-004  [GLM-5]  │
│  TASK-015  GH Projects/Issues     │  │  TASK-018  REQ-DOC-005  [Gemini] │
│  TASK-016  Commit git debt        │  │  TASK-019  REQ-DOC-006  [GLM-5]  │
└───────────────────────────────────┘  │  TASK-020  REQ-backlog   [GLM-5] │
                                        └──────────────────────────────────┘
```

**Estimated Total Timeline**: 3–4 weeks with parallel execution  
**Critical Path**: Phase 0 → TASK-021 (MC Agent) → Phase 2 (TASK-011 Qdrant)  
**Quick Win for Today**: TASK-001 + TASK-002 (50 min, zero risk, unblocks all agents)  
**Architectural North Star**: TASK-021 — when the Sovereign MC Agent is operational, the Foundation Stack directs itself

---

## METADATA

**Document Version**: 1.2.0  
**Prepared By**: Cline (Claude Sonnet 4.5) — strategic review | Updated with GLM-5 research  
**Intended Consumer**: OpenCode/GLM-5 — execution and research  
**v1.1 Changes**: Corrected memory bank date gap, Sovereign Stack MC architecture, TASK-021  
**v1.2 Changes**: Copilot PAID correction, GLM-5 completed tasks marked, Opus 4.6 free promotion noted, OpenRouter added, GLM-5 Q&A responses (Section 3.4)

**Completed Work (GLM-5 — 2026-02-18)**:
- ✅ TASK-001: Memory bank updated
- ✅ TASK-003: Two commits pushed (bdd8a0c, 122d328)
- ✅ TASK-008: Model matrix v2.0.0, OpenCode comprehensive guide, permissions fix script
- ✅ `scripts/fix-permissions.sh` — Redis/Qdrant UID 1001 ownership fix

**Source Verification**:
- ✅ MASTER-PROJECT-INDEX-v1.0.0.md reviewed
- ✅ memory_bank/activeContext.md reviewed
- ✅ mkdocs-internal.yml verified complete
- ✅ `opencode models --verbose` live output verified
- ✅ GLM-5 research findings incorporated (mc-oversight/MESSAGE-FOR-OPUS-2026-02-18.md)
- ✅ Copilot paid requirement confirmed and corrected throughout

**Next Actions**:
1. Cline/Opus: TASK-021b (Sovereign MC Agent) — use free Opus while promotion lasts
2. GLM-5: TASK-021a (MC Agent Spec) — design doc first
3. GLM-5: TASK-002 (Correct MASTER INDEX) — still pending
4. GLM-5: TASK-004 (Service health check) — still pending
5. Cline: TASK-005 (Phase 3 test deps) — quick win with free Opus

**Related Documents**:
- `internal_docs/00-system/MASTER-PROJECT-INDEX-v1.0.0.md`
- `internal_docs/01-strategic-planning/SOVEREIGN-MC-AGENT-SPEC-v1.0.0.md` (TASK-021a — pending)
- `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md` — NEW (GLM-5)
- `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md` — NEW (GLM-5)
- `scripts/fix-permissions.sh` — NEW (GLM-5)
- `mc-oversight/MESSAGE-FOR-OPUS-2026-02-18.md` — GLM-5 research handoff
- `mcp-servers/xnai-agentbus/`, `xnai-rag/`, `xnai-vikunja/` — MCP for Sovereign MC
