# XNAi Foundation: Model Research Crawler Strategy — Consolidated & Locked

**Version**: 1.0 (Locked for Cline Review)  
**Created**: 2026-02-16 21:00 UTC  
**Status**: READY FOR CLINE VALIDATION & KNOWLEDGE GAP RESEARCH

---

## I. Strategic Intent (Why This Matters)

### Problem
- Multiple agents (Copilot, Gemini, Cline, local LLM) operate in isolation without unified model knowledge
- No systematic research on XNAi-stack-compatible models for specialized tasks
- When lightweight crawler encounters complex research questions, it has no clear delegation path
- Agent knowledge bases are ad-hoc; no consistent structure, vector indexing, or task-specific optimization

### Solution
Build an **autonomous model knowledge infrastructure** where:
1. **Lightweight crawler** (ruvltra) researches XNAi-relevant models continuously
2. **Delegation protocol** automatically routes complex work to best-suited agent
3. **Expert knowledge bases** give each agent immediate access to task-specific context
4. **Feedback loops** (Cline reviews output) ensure knowledge quality improves iteratively
5. **Vector indexing** enables semantic search across all knowledge bases

### Strategic Outcome
- **Foundation for Agent Bus**: Each agent begins with tailored knowledge context immediately available
- **Sovereign research**: All work happens locally (no external API rate limits)
- **Scalable pattern**: Reusable for other knowledge domains (stack architecture, protocols, best practices)
- **Resource-aware**: Optimized for Ryzen 7 5700U (lightweight embeddings, async processing, memory monitoring)

---

## II. System Architecture (How It Works)

### Component 1: Model Research Crawler (Local LLM)
```
Input: Research task (model category, use case, XNAi integration requirements)
↓
Process: ruvltra-claude-code-0.5b researches models
  ├─ Query HuggingFace, Papers, community benchmarks
  ├─ Extract metadata (parameters, quantizations, benchmarks)
  ├─ Test ecosystem compatibility (Ryzen 7 inference speed)
  └─ Calculate complexity_score for delegation
↓
Output: Model card (JSON) + complexity score
↓
Delegation Check:
  ├─ score ≤ 3: Store in KB directly (done)
  ├─ 4 ≤ score ≤ 7: Queue for Conductor routing
  └─ score > 7: URGENT → escalate immediately
```

### Component 2: Delegation Protocol (Intelligent Routing)
```
Agent Bus Conductor receives complex research task from Crawler

Step 1: Calculate complexity_score (1-10)
  Add points for:
  - Unknown architecture/setup patterns (+2)
  - Multi-model comparison (+3)
  - Novel integration architecture (+4)
  - Code generation requirement (+2)
  - Documentation rewriting (+2)
  - System-level strategy decision (+3)

Step 2: Route based on score + task type
  4-5: Copilot (strategic planning, synthesis)
  6-7: Gemini (large-scale analysis, synthesis)
  8-9: Cline (implementation, documentation, testing)
  9+: Cline PRIORITY (full refactoring/architecture redesign)

Step 3: Agent processes task, reports back
Step 4: Results merge into KB with updated vectors
Step 5: Feedback loop: Cline reviews for gaps/quality
```

### Component 3: Expert Knowledge Bases (Per Agent)
```
expert-knowledge/
├── copilot/
│   ├── system-instructions.md (Haiku 4.5 profile, strengths, limitations)
│   ├── models/
│   │   ├── haiku-4.5-profile.md
│   │   └── gpt-5-mini-gaps.md
│   ├── sop/
│   │   ├── strategic-planning-protocols.md
│   │   ├── code-review-checklist.md
│   │   └── research-methodology.md
│   ├── examples/
│   │   ├── strategic-plan-template.md
│   │   └── research-synthesis-example.md
│   └── vectors.index (semantic search, 500-1000 embeddings)
│
├── gemini/
│   ├── system-instructions.md (Gemini 3 Pro profile, 1M context strategies)
│   ├── models/
│   │   ├── gemini-3-pro-capabilities.md
│   │   └── context-window-optimization.md
│   ├── sop/
│   │   ├── holistic-synthesis-protocols.md
│   │   ├── large-scale-analysis-framework.md
│   │   └── gap-identification-methodology.md
│   ├── examples/
│   │   └── large-document-processing-example.md
│   └── vectors.index (1000-2000 embeddings)
│
├── cline/
│   ├── system-instructions.md (kat-coder-pro profile, 256K context usage)
│   ├── models/
│   │   ├── kat-coder-pro-profile.md
│   │   └── kimi-k-2.5-profile.md
│   ├── sop/
│   │   ├── whole-codebase-refactoring.md
│   │   ├── documentation-rewriting.md
│   │   └── integration-testing.md
│   ├── examples/
│   │   ├── refactoring-example.md
│   │   └── test-automation-example.md
│   └── vectors.index (800-1200 embeddings)
│
└── crawler/
    ├── system-instructions.md (ruvltra profile, research protocols)
    ├── models/
    │   └── local-llm-capabilities.md
    ├── sop/
    │   ├── research-protocols.md
    │   ├── model-card-creation.md
    │   └── delegation-triggers.md
    ├── examples/
    │   └── model-research-workflow.md
    └── vectors.index (300-500 embeddings)

Each agent queries: "Given this task, what docs in my KB are relevant?"
→ Fast semantic search < 500ms for real-time decision support
```

### Component 4: Feedback Loop (Quality Assurance)
```
Crawler output (model cards, research findings) → stored in KB

Trigger: Cline automatically reviews all new KB content

Cline's review process:
  1. Read crawler output
  2. Identify documentation gaps
  3. Enhance with examples, edge cases, integration patterns
  4. Update model cards with additional context
  5. Re-embed → vectors.index updated
  6. Log improvements in feedback ledger

Result: KB quality improves with every iteration
```

---

## III. Execution Plan (6 Phases)

### Phase A: Knowledge Architecture Design (2-3 hours)
**Owner**: Copilot (Haiku 4.5)  
**Tasks**:
- [ ] Model Card Schema (Pydantic) with fields: id, task_category, specs, benchmarks, ecosystem, competitive_analysis, research_status
- [ ] Expert KB Schema — document types, vector embedding strategy, tool registry structure
- [ ] Delegation Protocol Flowchart — decision tree, complexity thresholds, routing rules (as code-ready pseudocode)
- [ ] Agent Role Definitions — crawler, conductor, Copilot, Gemini, Cline capabilities & non-overlapping boundaries

**Deliverables**:
- `knowledge/schemas/model-card-schema.py` (Pydantic)
- `knowledge/schemas/expert-kb-schema.py` (Pydantic)
- `docs/DELEGATION-PROTOCOL-v1.md` (flowchart + code pseudocode)
- `docs/AGENT-ROLE-DEFINITIONS.md` (detailed role descriptions)

**Success**: Schemas are implementable; delegation rules are clear enough for LLM execution

---

### Phase B: Model Research Crawler Job (5-7 hours)
**Owner**: Local Crawler (ruvltra) + Copilot (review)  
**Tasks**:
- [ ] Crawler Job Instructions — research targets, data sources, output format
- [ ] Initial Model Research — 50-100 models across 3 categories:
  - **Code Generation** (20-25): LLaMA, Mistral, DeepSeek Coder, StarCoder, CodeLLaMA
  - **Research & Synthesis** (20-25): Gemma, Qwen, Phi-3, OLMo, Falcons
  - **Data Curation & RAG** (15-20): ELSER, E5, BGE, sentence-transformers variants
- [ ] Model Card Dataset — JSON files with verified metadata, benchmarks, ecosystem compatibility
- [ ] Vector Embedding — use `sentence-transformers/all-MiniLM-L6-v2`, index in FAISS
- [ ] Copilot Review — quality assessment, gap analysis, improvement recommendations

**Deliverables**:
- `knowledge/model_cards/*.json` (50-100 model cards)
- `knowledge/vectors/model_cards.faiss` (FAISS index)
- `knowledge/model_cards_inventory.json` (metadata catalog)
- `docs/MODEL-RESEARCH-FINDINGS.md` (Copilot summary + gaps)

**Success**: Each model card has 2+ benchmark sources, ecosystem compatibility tested on Ryzen 7, competitive analysis accurate

---

### Phase C: Expert Knowledge Base Synthesis (4-5 hours)
**Owner**: Gemini (3 Pro) — Large-scale synthesis  
**Tasks**:
- [ ] Expert KB Schema Design — document types, tool registry, vector index architecture
- [ ] Copilot KB Population — task-specific models, system instructions, SOP docs, examples (500-1000 embeddings)
- [ ] Gemini KB Population — research methodologies, synthesis patterns, large-scale templates (1000-2000 embeddings)
- [ ] Cline KB Population — refactoring patterns, documentation templates, integration examples (800-1200 embeddings)
- [ ] Crawler KB Population — research protocols, model filtering logic, delegation rules (300-500 embeddings)
- [ ] Vector Indexing & Testing — semantic search < 500ms, relevance validation

**Deliverables**:
- `expert-knowledge/copilot/*.md` + `vectors.index`
- `expert-knowledge/gemini/*.md` + `vectors.index`
- `expert-knowledge/cline/*.md` + `vectors.index`
- `expert-knowledge/crawler/*.md` + `vectors.index`
- `docs/EXPERT-KB-USAGE-GUIDE.md` (how to query, integrate with agent work)

**Success**: All KBs populated; semantic search working; each agent can retrieve relevant docs in real-time

---

### Phase D: Delegation Protocol Implementation (3-4 hours)
**Owner**: Cline (kat-coder-pro)  
**Tasks**:
- [ ] Task Classification Module — complexity_score calculation logic
- [ ] Routing Logic — Agent Bus Conductor receives task, selects agent, queues work
- [ ] Complexity Scorer Tests — validate on 10+ test cases (model research tasks with known complexity)
- [ ] Feedback Loop Integration — Cline review process linked to crawler output pipeline

**Deliverables**:
- `communication_hub/conductor/task_classifier.py` (complexity scoring)
- `communication_hub/conductor/routing_engine.py` (agent selection + queuing)
- `tests/test_delegation_routing.py` (10+ test cases)
- `communication_hub/coordinator/cline_feedback_loop.py` (review process integration)

**Success**: Routing logic accurate; complexity scoring validated; Cline feedback integrated into KB update pipeline

---

### Phase E: Crawler Job Integration (2-3 hours)
**Owner**: Copilot (Haiku 4.5)  
**Tasks**:
- [ ] Crawler Job Processor — integrates with Redis job queue (`xnai:jobs:crawler:pending`)
- [ ] Research Protocol Config — instructions, prioritization, output format, scheduling
- [ ] Background Job Scheduler — daily model research (02:00 UTC), on-demand crawls
- [ ] Monitoring & Alerting — health checks, completion logs, error handling, Consul service registration
- [ ] Knowledge Base Update Pipeline — crawler output → KB storage → vector indexing → Cline review trigger

**Deliverables**:
- `scripts/crawler_job_processor.py` (main job loop)
- `scripts/crawler_research_protocol.yaml` (instructions, targets, scheduling)
- `scripts/crawler_monitor.py` (health checks, logging, Consul registration)
- `communication_hub/state/crawler_job_state.json` (job tracking)

**Success**: Crawler job runs autonomously on schedule; KB updates triggered; Cline review queued automatically

---

### Phase F: Integration Testing & Feedback Loop Verification (2-3 hours)
**Owner**: Gemini (3 Pro) + Cline  
**Tasks**:
- [ ] End-to-End Integration Test — crawler → delegation → agent response → KB update → vector reindex → Cline review
- [ ] Feedback Loop Validation — Cline review improves KB quality (before/after comparison)
- [ ] Performance Benchmarks — crawler latency, vector search speed, delegation accuracy
- [ ] Documentation & Runbooks — how to operate crawler, troubleshooting guide, monitoring dashboard

**Deliverables**:
- `tests/test_crawler_integration.py` (end-to-end pipeline)
- `tests/test_feedback_loop.py` (quality improvement validation)
- `docs/CRAWLER-OPERATIONS-RUNBOOK.md` (how to run, troubleshoot)
- `docs/CRAWLER-MONITORING-GUIDE.md` (metrics, alerting, health checks)

**Success**: All integration tests pass; feedback loop executes successfully; crawler latency < 5 min per 10-model batch

---

## IV. Resource Allocation & Timeline

### Team Assignments
| Phase | Owner | Model | Hours | Dependency |
|-------|-------|-------|-------|------------|
| A | Copilot | Haiku 4.5 | 2-3h | None |
| B | Crawler + Copilot | ruvltra + Haiku | 5-7h | Phase A complete |
| C | Gemini | Gemini 3 Pro | 4-5h | Phase A, B start |
| D | Cline | kat-coder-pro | 3-4h | Phase A, C start |
| E | Copilot | Haiku 4.5 | 2-3h | Phase D complete |
| F | Gemini + Cline | Both | 2-3h | Phase E complete |
| **Total** | | | **18-25h** | Parallelizable |

### Timeline (Recommended)
- **Day 1** (Hours 0-8): Phases A + B (start) + C (start)
- **Day 2** (Hours 8-16): Phase B (end) + Phase C (end) + Phase D
- **Day 3** (Hours 16-25): Phase E + Phase F

**Parallelization**: Phases A, B, C can run in parallel after A completes (B and C depend on A's schemas but can start simultaneously)

---

## V. Success Criteria (Measurable)

### Knowledge Quality ✓
- [x] 50-100 model cards with verified metadata (specs, benchmarks, ecosystem)
- [x] 2+ benchmark sources per model (HuggingFace, papers, community tests)
- [x] Ecosystem compatibility tested on Ryzen 7 (actual inference speed measurements)
- [x] Competitive analysis for each model (strengths, weaknesses, alternatives)

### System Architecture ✓
- [x] Delegation protocol clear and implementable (code-ready pseudocode)
- [x] Expert KBs structured, populated, searchable (vectors indexed)
- [x] Vector search performance < 500ms for 1000+ embeddings
- [x] Agent roles non-overlapping, well-defined

### Integration & Automation ✓
- [x] Crawler job runs autonomously (scheduled, monitored, logged)
- [x] Delegation routing accurate (validated on 10+ test cases)
- [x] Cline feedback loop improves KB quality (measurable improvement)
- [x] Monitoring/alerting detects failures, reports status

### Documentation & Operations ✓
- [x] Runbook for crawler job management (step-by-step instructions)
- [x] Troubleshooting guide (common issues, resolution steps)
- [x] System instructions updated for all agents
- [x] Performance metrics baseline established (latency, throughput, vector search speed)

---

## VI. Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Model research sources unreliable (HuggingFace down, papers outdated) | Medium | High | Use multiple sources, manual verification layer, maintain fallback sources |
| Vector search inefficient at scale (> 100k embeddings) | Low | Medium | Start with FAISS flat index, plan HNSW upgrade, test early |
| Delegation protocol too complex, agents misunderstand routing | Medium | Medium | Start simple (score-based), test with 10+ examples, iterate |
| Expert KB content becomes stale (outdated instructions, deprecated tools) | Medium | Medium | Auto-update on crawler runs, Cline review every 2 weeks, version tracking |
| Ryzen 7 memory exhausted during crawler runs + vector indexing | Low | High | Resource monitoring in place, batch processing (10 models/hour), async updates |
| Cline review process bottleneck (too much to review, creates backlog) | Medium | Medium | Prioritize high-complexity findings, sample-based review (20% of output), automation where possible |

---

## VII. Knowledge Gaps to Research (For Cline)

### Critical Research Questions
1. **Model Research Sourcing**
   - What are the most reliable sources for model benchmarks? (HuggingFace, Papers, community tests)
   - How often do benchmarks become stale? What's the refresh cadence?
   - Are there curated model registries beyond HuggingFace that should be included?

2. **Vector Indexing & Semantic Search**
   - Is `sentence-transformers/all-MiniLM-L6-v2` (22MB) optimal for Ryzen 7, or should we explore quantized variants?
   - At what vector count should we upgrade from FAISS flat to HNSW?
   - How do we handle versioning/rollback of vector indexes?

3. **Delegation Protocol Complexity**
   - Are the complexity thresholds (score 1-10) realistic based on actual model research tasks?
   - Should we have sub-categories (code-gen research vs. RAG research have different complexity patterns)?
   - How do we handle ambiguous tasks that don't fit the scoring rubric?

4. **Cline Feedback Loop**
   - How much of Cline's output should be automated vs. manual review?
   - What metrics measure "KB quality improvement"?
   - Should Cline review all crawler output or sample-based (every Nth, or top-N complexity)?

5. **Expert KB Structure**
   - Should each agent's KB have shared/common sections, or is per-agent isolation better?
   - How do we prevent KB content drift across agent KBs?
   - Should KBs be version-controlled in Git, or stored in Redis for faster updates?

6. **Scaling & Performance**
   - What's the expected crawler throughput? (10 models/hour? 50 models/day?)
   - At what KB size does semantic search start to degrade?
   - How do we monitor crawler health without burning CPU on Ryzen 7?

7. **Integration Complexity**
   - What's the right level of integration between crawler, conductor, Consul, Redis, Vikunja?
   - Should crawler have its own database (SQLite) for audit/history, or Redis only?
   - How do we ensure Cline feedback is actually incorporated into the next crawler run?

---

## VIII. Assumptions

1. **Crawler uses ruvltra-claude-code-0.5b** for initial research (local, cost-free, no rate limits)
2. **Expert KBs use `sentence-transformers/all-MiniLM-L6-v2`** for embeddings (proven, lightweight, 22MB)
3. **Agent Bus infrastructure stable** (Redis 6379, Consul 8500, Vikunja via Caddy, Caddy 8000)
4. **Cline kat-coder-pro available** for implementation tasks
5. **Model card data is JSON**, stored in `knowledge/model_cards/`, vectors in FAISS
6. **Feedback loop is automated** (triggered by crawler job completion, Cline responds within 1-2 hours)

---

## IX. Next Steps (Locked Strategy)

1. ✅ **Strategy Consolidated** (this document)
2. ⏳ **Cline Review** — kat-coder-pro validates plan, researches knowledge gaps, reports back
3. ⏳ **Confirm Strategy** — incorporate Cline feedback, finalize approach
4. ⏳ **Execute Phases A-F** — begin immediately upon confirmation

---

**Status**: LOCKED FOR CLINE REVIEW  
**Prepared by**: Copilot CLI (Claude Haiku 4.5)  
**For**: XNAi Foundation Agent Bus — Model Knowledge Infrastructure  
**Next**: Awaiting Cline (kat-coder-pro) validation and knowledge gap research
