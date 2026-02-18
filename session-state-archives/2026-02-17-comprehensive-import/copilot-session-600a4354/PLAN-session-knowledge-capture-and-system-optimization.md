---
title: "Session Knowledge Capture & System Optimization Strategy"
created: "2026-02-16T20:10:00Z"
status: "PLAN MODE - AWAITING USER APPROVAL"
phase: "XOH Infrastructure Hardening + Documentation Refresh + Agent Bus Orchestration"
---

# Plan: Session Knowledge Capture, Documentation Refresh, & Autonomous Agent Orchestration

## 📋 PROBLEM STATEMENT

Current state:
- Infrastructure hardening session completed (Redis, Vikunja, Consul, Caddy verified)
- Knowledge captured in session artifacts but not yet integrated into system
- README.md severely outdated (no mention of Agent Bus, Vikunja, memory_bank, tool suite)
- memory_bank exists but sparse and not optimized for agent use
- Agent Bus exists but orchestration strategy is undefined
- Background research/automation has no scheduling, priority, or resource management
- No automated knowledge capture protocol (learnings from sessions not systematized)

Goal:
- Capture this session's learnings into reusable protocols and best practices
- Modernize README with current features, tool suite, and community engagement
- Optimize memory_bank for agent reference and onboarding
- Design scalable autonomous agent orchestration that respects resource constraints
- Create system for continuous knowledge capture and SOP refinement

## 🎯 APPROACH OVERVIEW

**Phase A: Knowledge Extraction & Capture** (Copilot + Cline plan mode)
- Extract learnings from session (infrastructure topology, troubleshooting, blockers)
- Convert to reusable protocols, SOPs, and best practices
- Organize into expert-knowledge/ and internal_docs/

**Phase B: README & Marketing** (Copilot + Cline plan mode)
- Comprehensive audit of current README
- Rewrite with focus on: core features (#1), tool suite (#2), unique value props
- Highlight: no-telemetry, torch-free, local-first, community-friendly
- Add architecture diagrams, quick-start guide, contribution guidelines
- Mention planned features (Ancient Greek expertise, etc.)

**Phase C: Memory Bank Optimization** (Copilot + Cline plan mode)
- Audit current memory_bank entries
- Add missing: service architecture, Agent Bus design, protocols, tool guides
- Structure for easy agent reference and onboarding
- Create index and cross-links

**Phase D: Agent Orchestration Strategy** (Gemini research + Copilot planning)
- Research ZeroClaw agent framework (check GitHub link user provided)
- Design orchestration layer addressing:
  - Resource constraints (Ryzen 7 5700U with 6.6GB RAM)
  - Rate limiting (Copilot free tier, Gemini free tier)
  - Task queuing and prioritization
  - Model load balancing (local GGUF + CLI models)
  - System resource monitoring and throttling
  - Background job scheduling
- Propose lightweight orchestrator (possibly using ruvltra-claude-code-0.5b-q4_k_m.gguf)
- Define delegation strategy: local LLM → Copilot (Haiku) → Gemini (complex)
- Create SOP for background process management

**Phase E: Protocol & SOP Documentation** (Copilot)
- Document infrastructure troubleshooting protocols (Redis, Vikunja, Qdrant, etc.)
- Create Agent Bus operational runbooks
- Define agent task prioritization and delegation rules
- SOP for background research job management
- SOP for knowledge capture from sessions
- SOP for continuous protocol refinement

**Phase F: Background Automation Setup** (Cline execution)
- Implement system resource monitor (check memory, CPU before spawning jobs)
- Create background research queue/scheduler
- Set up Copilot (Haiku) as default research agent
- Configure local LLM to always have a research job queued
- Create switchboard to pause/resume jobs based on resource usage
- Implement lightweight orchestrator skeleton

## 📊 DETAILED WORKPLAN

### Phase A: Knowledge Extraction (Copilot Plan Mode) — 2-3 hours

**Task A1: Session Learnings Analysis**
- [ ] Review SESSION-FINAL-REPORT.md and this session's findings
- [ ] Extract key discoveries: Vikunja routing, Redis auth syntax, Qdrant uid/gid, service topology
- [ ] Categorize: infrastructure troubleshooting, architecture decisions, security/sovereignty practices

**Task A2: Convert to Reusable Protocols**
- [ ] **Troubleshooting Protocol: Redis Auth Issues** → expert-knowledge/redis-troubleshooting.md
- [ ] **Architecture Pattern: Reverse Proxy Isolation** → expert-knowledge/caddy-service-isolation-pattern.md
- [ ] **SOP: Multi-Container Permission Management** → internal_docs/00-project-standards/container-uid-gid-strategy.md
- [ ] **Best Practice: Service Topology Design** → expert-knowledge/service-topology-design-best-practices.md
- [ ] **Integration Guide: Vikunja Task Scheduling** → expert-knowledge/vikunja-integration-guide.md

**Task A3: Update Stack Protocols**
- [ ] Review and enhance: COPILOT-CUSTOM-INSTRUCTIONS.md (add Redis/Vikunja protocols)
- [ ] Create: INFRASTRUCTURE-MAINTENANCE-RUNBOOK.md (for ops team)
- [ ] Create: AGENT-BUS-OPERATIONAL-GUIDE.md (for Agent Bus operators)

**Deliverables**:
- 5 new expert-knowledge files
- 2 new internal_docs protocol files
- Updated custom instructions with infrastructure knowledge

---

### Phase B: README Modernization (Copilot Plan Mode) — 3-4 hours

**Task B1: Current State Audit**
- [ ] Review current README.md (what exists now)
- [ ] Identify gaps vs. Phase A knowledge
- [ ] List sections that need rewriting vs. new sections

**Task B2: Core Features Rewrite (#1 Priority)**
- [ ] Agent Bus: distributed, multi-agent, zero-trust architecture
- [ ] Service architecture: Redis (state), Consul (discovery), Caddy (routing), Vikunja (workflows)
- [ ] Multi-model support: Copilot CLI, Gemini CLI, local LLMs (sovereign compute)
- [ ] Data stack: FAISS + Redis + Qdrant (redundant vector/semantic search)
- [ ] Sovereignty: zero-telemetry, local-first, torch-free, no cloud dependencies

**Task B2: Tool Suite Documentation (#2 Priority)**
- [ ] XNAi Agent Bus: task coordination, state persistence, service discovery
- [ ] Copilot CLI: research agent (Haiku), coordination, documentation
- [ ] Gemini CLI: complex research (Gemini 3 Pro, 1M context), holistic analysis
- [ ] Cline CLI: code execution, refactoring, integration testing
- [ ] Local LLMs: sovereign compute, long-running jobs, embeddings
- [ ] memory_bank: agent reference, architecture docs, protocols
- [ ] Vikunja integration: task scheduling, workflow coordination
- [ ] Health check tools: stack_health_check.sh, redis_health_check.py
- [ ] Mention: FAISS, Redis, Qdrant, mmap strategies, resource optimization

**Task B3: Unique Value Props**
- [ ] No telemetry by design
- [ ] Torch-free (GGUF-based, local LLMS)
- [ ] Ancient Greek expertise (planned feature, attracts scholarly community)
- [ ] Community-focused: encourage contributions, reuse, repurposing
- [ ] Scalable from single-user (Ryzen 7) to cluster deployments

**Task B4: Architecture & Quick-Start**
- [ ] Add architecture diagram (services, networks, data flow)
- [ ] Quick-start: `make up`, access Vikunja, run health check
- [ ] Contributing guide: how to add protocols, tools, expertise domains
- [ ] Links to: internal_docs/, memory_bank/, expert-knowledge/

**Deliverables**:
- Modernized README.md (2000+ words, comprehensive)
- Quick-start section
- Contributing guide
- Architecture diagram (text or reference to visual)

---

### Phase C: Memory Bank Optimization (Copilot Plan Mode) — 1-2 hours

**Task C1: Current State Audit**
- [ ] List existing memory_bank/ entries
- [ ] Identify gaps (missing: architecture, protocols, tool guides, best practices)

**Task C2: Add Essential Entries**
- [ ] `xnai_agent_bus_architecture.md` — full design, APIs, state persistence
- [ ] `agent_coordination_protocols.md` — how agents talk to each other
- [ ] `task_prioritization_and_delegation.md` — when to use local LLM vs Copilot vs Gemini
- [ ] `resource_management_strategy.md` — how to balance CPU/RAM with concurrent jobs
- [ ] `background_research_job_queue.md` — how to queue and schedule long-running jobs
- [ ] `infrastructure_architecture.md` — Redis, Consul, Caddy, Vikunja, Qdrant topology
- [ ] `tool_quick_reference.md` — Copilot CLI, Gemini CLI, Cline CLI cheat sheet
- [ ] `troubleshooting_index.md` — links to all troubleshooting guides

**Task C3: Optimize Structure**
- [ ] Create `memory_bank/00-INDEX.md` (navigation guide)
- [ ] Add cross-links between entries
- [ ] Ensure AI-readability (consistent formatting, clear structure)
- [ ] Add timestamps and version info for each entry

**Deliverables**:
- 8 new memory_bank entries
- Updated index with cross-links
- AI-optimized formatting

---

### Phase D: Agent Orchestration Strategy (Gemini Research + Copilot Planning) — 4-6 hours

**Task D1: ZeroClaw Framework Research** (Gemini CLI, plan mode)
- [ ] Fetch and analyze: https://github.com/zeroclaw-labs/zeroclaw
- [ ] Assess: Can it manage multiple agents (Copilot, Gemini, Cline, local LLM)?
- [ ] Assess: Does it support rate limiting, resource constraints, task queuing?
- [ ] Assess: Would adapting it be faster than building custom orchestrator?
- [ ] Research: Alternative agent frameworks for resource-constrained environments
- [ ] Deliverable: ZeroClaw feasibility report + alternatives analysis

**Task D2: Design Agent Orchestration Layer** (Copilot plan mode, informed by Gemini research)
- [ ] **Architecture Decision**:
  - Option A: Adapt ZeroClaw (if feasible from Gemini analysis)
  - Option B: Lightweight custom orchestrator using ruvltra-claude-code-0.5b-q4_k_m.gguf
  - Option C: Hybrid (ZeroClaw core + custom XNAi layer)
  - Recommend: Build on existing Agent Bus (Consul + Redis) rather than new framework

- [ ] **Resource Management**:
  - System monitor: Check `/proc/meminfo`, CPU load before spawning jobs
  - Thresholds: Pause background jobs if RAM < 2GB or CPU > 70%
  - Auto-resume when resources available again

- [ ] **Task Queuing & Prioritization**:
  - Queue: Redis streams or Vikunja tasks
  - Priority levels: CRITICAL (block all), HIGH (pause long-running), NORMAL, LOW
  - FIFO within priority level

- [ ] **Model Load Balancing**:
  - **Always available** (no rate limit): ruvltra-claude-code-0.5b-q4_k_m.gguf
  - **On-demand cheap** (Copilot Haiku): Daily research, trivial tasks, quick synthesis
  - **On-demand expensive** (Gemini 3 Pro): Complex analysis, large-context synthesis, system design
  - **Offloading strategy**:
    - Local LLM starts task, estimates complexity
    - If < 30 min local, run locally; else queue for Copilot
    - If > 100k tokens or needs 1M context, assign to Gemini
    - Copilot acts as "middle tier" — balancer and executor

- [ ] **Background Job Scheduling**:
  - **Always-on**: Local LLM research queue (one job at a time, rotate)
  - **During work hours** (08:00-20:00): Copilot research agent, Cline experiments
  - **During idle** (20:00-08:00): Heavy Cline refactoring, Gemini complex synthesis
  - **On-demand**: Pause background for foreground interactive work

- [ ] **Delegation Strategy**:
  ```
  Request arrives → ruvltra task router (lightweight)
    ├─ Simple (< 5 min, < 10k tokens) → local LLM
    ├─ Medium (5-30 min, 10-100k tokens) → Copilot (Haiku)
    ├─ Complex (> 30 min, > 100k tokens) → Gemini (or Cline for code)
    └─ System-wide (architecture, multi-component) → Gemini 3 Pro
  ```

- [ ] **Self-Delegation Protocol**:
  - Agents can propose tasks to orchestrator
  - Examples: "I need Gemini to analyze X", "Queue research job Y"
  - Orchestrator validates, checks resources, queues or runs

---

### **Phase D-BONUS: CLI Agent Research & System Instructions** (Gemini Research + Copilot Planning) — 5-7 hours
**CRITICAL ADDITION**: Optimize agent performance by understanding each CLI's unique capabilities, quirks, and model strengths

**Task D-BONUS-1: Gemini CLI Deep Research** (Gemini CLI, plan mode)
- [ ] **Capabilities audit**:
  - Available models: Gemini 3 Pro, Gemini 3.5-Sonnet, Gemini 3.5-Haiku, Gemini 2.0 Flash (if available)
  - Context windows and token limits for each model
  - Tool calling behavior and API specifics
  - Rate limiting, quota management, free tier limitations
  - Strengths/weaknesses compared to alternatives

- [ ] **Unique quirks & optimization**:
  - How does Gemini 3 Pro handle large context? (1M window)
  - Does it prefer structured JSON for tool calling?
  - Any latency considerations for large research tasks?
  - How does it compare to Claude for code analysis?
  - Best use cases and anti-patterns

- [ ] **System instructions for Gemini CLI**:
  - When to use Gemini 3 Pro vs 3.5-Sonnet vs 3.5-Haiku
  - How to structure prompts for optimal synthesis
  - Tool calling patterns and expected response format
  - Batch processing for large document analysis (if supported)
  - Cost optimization strategies

- [ ] **Benchmark findings**:
  - Performance on: research tasks, code review, architecture design, multi-document synthesis
  - Comparison to Claude Opus, GPT-4 on same tasks (if available)
  - Optimal token usage per task type

**Task D-BONUS-2: Copilot CLI Deep Research** (Copilot CLI, plan mode)
- [ ] **Capabilities audit** (as of 2026-02-16):
  - Available models: Claude Haiku 4.5, GPT-5 mini, others?
  - User's findings: Haiku 4.5 = excellent planning/research/review, GPT-5 mini = lacking
  - Context windows, token limits
  - Tool calling and API specifics
  - Rate limiting and free tier constraints

- [ ] **Model analysis** (per your observations):
  - Claude Haiku 4.5: Why excels at planning? Structure? Training?
  - GPT-5 mini: Why lacking? Context size? Training?
  - Are there other models available (e.g., Claude Opus-4.6)?
  - Model selection logic for daily research tasks

- [ ] **System instructions for Copilot CLI**:
  - When to use Haiku 4.5 (default for daily research, planning, review)
  - When to escalate to Gemini (if using Opus/other model)
  - Prompt structure for optimal Haiku performance
  - Tool calling patterns and response format
  - Optimization for fast iteration (cheap tokens, fast responses)

- [ ] **Benchmark findings**:
  - Latency, accuracy, cost trade-offs
  - Comparison: Haiku vs GPT-5 mini vs Gemini 3.5-Haiku
  - Optimal task delegation (Haiku > Gemini for what?)

**Task D-BONUS-3: Cline CLI Deep Research** (Cline CLI or user research)
- [ ] **Available models**:
  - kat-coder-pro (256K context, excellent at docs/refactoring, per user)
  - moonshotai/kimi-k-2.5 (unknown, need to research)
  - Other available models in Cline ecosystem?
  - Context windows, capabilities per model

- [ ] **Model strengths/weaknesses**:
  - kat-coder-pro: Why excel at documentation and refactoring?
  - Does 256K context help with whole-codebase understanding?
  - Comparison to Claude/GPT for code tasks
  - Best use cases (refactoring, new features, test writing, docs)
  - Anti-patterns or known limitations

- [ ] **System instructions for Cline CLI**:
  - When to use kat-coder-pro vs kimi-k-2.5 vs other models
  - How to structure code prompts for optimal output
  - Tool calling patterns (git, file ops, execution)
  - Batch refactoring strategies
  - Testing and validation workflow

- [ ] **Integration with XNAi Agent Bus**:
  - How does Cline's tool calling interact with Agent Bus?
  - Optimal task format for Cline execution
  - Feedback loop and error handling

**Task D-BONUS-4: Lightweight Model Strategies** (Gemini research + Copilot planning)
- [ ] **Alternative lightweight models** (beyond ruvltra-claude-code-0.5b-q4_k_m.gguf):
  - **Mistral-7B** — fast, efficient, good for instruction following
  - **Llama-2-7B** — open-source baseline, widely tested
  - **Deepseek-Coder-6.7B** — specialized for code tasks
  - **Phi-2/Phi-3** — ultra-lightweight (2-3B), designed for inference efficiency
  - **OLMo** — open language model from AI2, optimized for research
  - **Qwen models** (Qwen-1.8B, Qwen-7B) — excellent efficiency

- [ ] **Ruvltra optimization strategies**:
  - Is ruvltra-claude-code-0.5b truly optimal?
  - Quantization analysis: q4_k_m vs q5_k_m vs q8? (speed vs quality)
  - mmap strategy for Ryzen 7 5700U (which memory layout optimal?)
  - Multi-model ensemble approach: when to use ruvltra vs switching to larger model

- [ ] **Hybrid deployment strategies**:
  - **Local-first cascade**: Try lightweight → escalate if fails → use Copilot/Gemini
  - **Model switching based on token budget**: Use ruvltra for < 10k tokens, escalate for larger
  - **Ensemble approach**: Use multiple small models in parallel, aggregate results
  - **Speculative decoding**: Small model drafts, large model refines
  - **Local model for routing**: Use ruvltra to classify task complexity, route to appropriate agent

- [ ] **VRAM and inference optimization**:
  - CPU vs GPU inference trade-offs on Ryzen 7 5700U
  - mmap benefits for avoiding full model load
  - KV cache optimization for long sequences
  - Batch inference strategies for queued tasks
  - How to measure inference time and optimize

- [ ] **Cost vs quality trade-offs**:
  - Compare: Local (free but slow) vs Copilot (cheap, fast) vs Gemini (expensive, best)
  - When does local model ROI exceed Copilot cost?
  - Optimal allocation of free tier tokens (Copilot + Gemini)

**Task D-BONUS-5: Create Dedicated System Instructions** (Copilot planning + Cline implementation)
- [ ] **Gemini CLI system instructions**:
  - File: `GEMINI-CLI-SYSTEM-INSTRUCTIONS.md`
  - Instructions for: research tasks, gap analysis, synthesis, architecture review
  - Model selection logic (Gemini 3 Pro for complex, 3.5-Haiku for quick, etc.)
  - Prompt templates for common tasks
  - Tool calling patterns and expected format

- [ ] **Copilot CLI system instructions**:
  - File: `COPILOT-CLI-SYSTEM-INSTRUCTIONS.md`
  - Instructions for: daily research, planning, code review
  - Focus on Haiku 4.5 (avoid GPT-5 mini unless necessary)
  - Prompt templates for fast iteration
  - Integration with Agent Bus

- [ ] **Cline CLI system instructions**:
  - File: `CLINE-CLI-SYSTEM-INSTRUCTIONS.md`
  - Instructions for: code refactoring, documentation, feature implementation
  - Model selection (kat-coder-pro default, kimi for certain tasks)
  - Whole-codebase refactoring workflow
  - Testing and validation patterns

- [ ] **Local LLM system instructions**:
  - File: `LOCAL-LLM-SYSTEM-INSTRUCTIONS.md`
  - Instructions for ruvltra and lightweight models
  - When to use locally vs escalate
  - Task classification (what ruvltra can handle)
  - Optimization for Ryzen 7 hardware

- [ ] **Model selection matrix**:
  - File: `MODEL-SELECTION-MATRIX.md`
  - Flowchart: task type → complexity → context size → model choice
  - Examples for common tasks: research, code, documentation, synthesis

**Task D-BONUS-6: Create Model Registry & Performance Baseline** (Copilot planning + Cline implementation)
- [ ] **Update memory_bank entry**: `available-models-and-capabilities.md`
  - All available models (local, Copilot, Gemini, Cline)
  - Context, speed, cost, ideal use cases
  - Performance baseline (latency, accuracy, token efficiency)

- [ ] **Create benchmarking framework**:
  - File: `scripts/model_benchmark.py`
  - Test each model on: planning task, research task, code task, documentation task
  - Measure: latency, token usage, quality
  - Store results in Redis for real-time optimization

- [ ] **Dynamic model selection** (optional):
  - Update task_router.py to use benchmark data
  - Recommend model based on current performance, not just complexity

**Deliverables**:
- ZeroClaw feasibility report (from Phase D Task 1)
- 3 detailed CLI research reports (Gemini, Copilot, Cline)
- Lightweight model analysis + ruvltra optimization recommendations
- Hybrid deployment strategy document
- 5 system instruction files (Gemini, Copilot, Cline, Local, Model Selection)
- Model registry and benchmarking framework
- Model selection matrix and decision flowchart

---
- [ ] Document: Agent types, capabilities, rate limits, cost
- [ ] Document: Resource constraints and monitoring
- [ ] Document: Task routing logic and priority levels
- [ ] Document: How agents request other agents
- [ ] Document: SOP for background job management

**Deliverables**:
- ZeroClaw feasibility report (from Gemini)
- Agent orchestration architecture design (5-10 pages)
- Resource management strategy
- Task routing and delegation flowchart
- Background job scheduler SOP

---

### Phase E: Protocols & SOP Documentation (Copilot) — 2-3 hours

**Task E1: Infrastructure Troubleshooting Protocols**
- [ ] Create: `internal_docs/00-project-standards/INFRASTRUCTURE-TROUBLESHOOTING-GUIDE.md`
  - Redis auth failures (use `-a` flag, not `-u`)
  - Vikunja routing (via Caddy, not direct port)
  - Qdrant uid/gid issues (requires elevated perms or data reset)
  - Service discovery failures (check Consul registration)
  - Disk space management (cleanup strategy for models/, embeddings/)
  - Network isolation issues (check docker networks)

**Task E2: Agent Bus Operational Runbooks**
- [ ] Create: `internal_docs/00-project-standards/AGENT-BUS-RUNBOOK.md`
  - Starting coordinator and watcher
  - Monitoring state persistence (Redis vs filesystem)
  - Handling failed tasks (retry logic, dead-letter queue)
  - Agent registration and handshake verification
  - Health checks and alerting

**Task E3: Task Prioritization & Delegation SOP**
- [ ] Create: `internal_docs/00-project-standards/AGENT-TASK-PRIORITIZATION-SOP.md`
  - When to use local LLM vs Copilot vs Gemini
  - Resource estimation heuristics
  - Priority levels and examples
  - Request format and SOP

**Task E4: Background Job Management SOP**
- [ ] Create: `internal_docs/00-project-standards/BACKGROUND-JOB-MANAGEMENT-SOP.md`
  - Job queue structure (Vikunja tasks or Redis streams)
  - Scheduling strategy (always-on, work hours, idle, on-demand)
  - Resource monitoring and auto-throttle
  - Pause/resume protocol
  - Job lifecycle (queue → assign → run → complete/fail)

**Task E5: Knowledge Capture & Session Protocol**
- [ ] Create: `internal_docs/00-project-standards/SESSION-KNOWLEDGE-CAPTURE-PROTOCOL.md`
  - What to document from each session
  - Format and structure (templates)
  - Review and extraction workflow
  - When to promote session artifacts to permanent docs
  - SOP for updating protocols based on learnings

**Task E6: Continuous Protocol Refinement**
- [ ] Create: `internal_docs/00-project-standards/PROTOCOL-REFINEMENT-PROCESS.md`
  - Who reviews and updates protocols
  - When protocols should be revisited
  - How to propose changes
  - Versioning and changelog

**Deliverables**:
- 6 comprehensive SOP documents (50-100 lines each)
- Checklists and templates for operators
- Cross-links to relevant memory_bank entries

---

### Phase F: Background Automation Implementation (Cline Execution) — 3-4 hours
*Note: Cline executes after plan approval; listed here for completeness*

**Task F1: System Resource Monitor**
- [ ] Create: `scripts/system_resource_monitor.py`
  - Check `/proc/meminfo`, `/proc/loadavg`
  - Publish thresholds to Redis (for agents to query)
  - Alert when RAM < 2GB or CPU > 70%

**Task F2: Background Job Queue**
- [ ] Implement: Queue in Redis streams or Vikunja
- [ ] Create: `scripts/background_job_processor.py`
  - Poll queue, check resources, dispatch to appropriate agent

**Task F3: Lightweight Task Router**
- [ ] Create: `scripts/task_router.py` (uses ruvltra-claude-code-0.5b-q4_k_m.gguf)
  - Lightweight classification of incoming requests
  - Route to local LLM, Copilot, or Gemini
  - Check resource availability before assignment

**Task F4: Integration with Agent Bus**
- [ ] Update: `scripts/agent_coordinator.py`
  - Add resource check before accepting new tasks
  - Implement pause/resume based on system state
  - Support self-delegation (agents requesting other agents)

**Deliverables**:
- 3 new Python scripts (monitoring, queue, router)
- Updated agent_coordinator.py with resource awareness
- Integration tests

---

## 🗂️ FILE ORGANIZATION PLAN

### Created/Modified by This Plan

**New expert-knowledge/ entries:**
- `redis-troubleshooting.md`
- `caddy-service-isolation-pattern.md`
- `vikunja-integration-guide.md`
- `service-topology-design-best-practices.md`

**New internal_docs/ entries:**
- `00-project-standards/INFRASTRUCTURE-TROUBLESHOOTING-GUIDE.md`
- `00-project-standards/AGENT-BUS-RUNBOOK.md`
- `00-project-standards/AGENT-TASK-PRIORITIZATION-SOP.md`
- `00-project-standards/BACKGROUND-JOB-MANAGEMENT-SOP.md`
- `00-project-standards/SESSION-KNOWLEDGE-CAPTURE-PROTOCOL.md`
- `00-project-standards/PROTOCOL-REFINEMENT-PROCESS.md`
- `00-project-standards/container-uid-gid-strategy.md`

**Updated:**
- `README.md` (major rewrite, 2000+ words)
- `COPILOT-CUSTOM-INSTRUCTIONS.md` (add infrastructure knowledge)
- `memory_bank/` (8 new entries + INDEX.md)

**New scripts:**
- `scripts/system_resource_monitor.py`
- `scripts/background_job_processor.py`
- `scripts/task_router.py`

**Total New Files:** 20+  
**Total Modified Files:** 4  
**Estimated Lines Added:** 3000+

---

## 🎯 SUCCESS CRITERIA

- ✅ Session learnings systematized into reusable protocols
- ✅ README modernized with focus on core features + tool suite
- ✅ memory_bank optimized for agent onboarding and reference
- ✅ Agent orchestration strategy designed (with resource management)
- ✅ SOPs documented for infrastructure, Agent Bus, background jobs
- ✅ Continuous improvement process defined
- ✅ All changes committed to git with clear messaging

---

## ⏱️ EFFORT ESTIMATE

| Phase | Effort | Notes |
|-------|--------|-------|
| A: Knowledge Extraction | 2-3 hrs | Copilot plan mode |
| B: README Modernization | 3-4 hrs | Copilot + Cline plan mode |
| C: Memory Bank Optimization | 1-2 hrs | Copilot plan mode |
| D: Agent Orchestration | 4-6 hrs | Gemini research + Copilot planning |
| **D-BONUS: CLI & Model Research** | **5-7 hrs** | **Gemini deep research + system instructions** |
| E: Protocol Documentation | 2-3 hrs | Copilot plan mode |
| F: Implementation | 3-4 hrs | Cline execution |
| **TOTAL** | **20-29 hrs** | **Parallelizable; recommend 2-3 parallel teams** |

**Recommended Parallelization:**
- **Team 1** (Copilot): A, B, C, E (8-14 hrs serial, or 4-7 hrs if parallel with team 2)
- **Team 2** (Gemini): D + D-BONUS (9-13 hrs, critical research phase)
- **Team 3** (Cline): F (3-4 hrs, after plan approval)

---

## 📋 NEXT STEP: USER APPROVAL

**Before switching to act mode, please confirm:**

1. **Scope**: Does this plan cover everything you wanted?
   - Knowledge capture from session? ✓
   - README update with focus on core features + tools? ✓
   - Memory bank optimization? ✓
   - Agent orchestration strategy? ✓
   - Protocol & SOP documentation? ✓

2. **Approach**: Do you agree with the phases and delegation?
   - Use plan mode on Copilot/Gemini/Cline to develop strategies first? ✓
   - Copilot as primary strategist + executor?
   - Gemini for complex research (ZeroClaw, alternatives)?
   - Cline for implementation once plan approved?

3. **Background Automation**: Does the orchestration strategy address your needs?
   - Local LLM always has a research job queued? ✓
   - Copilot (Haiku) for daily research?
   - Gemini for complex/large-scale tasks?
   - Resource monitoring and auto-throttle?
   - Self-delegation protocol for agents?

4. **Priorities**: Any adjustments to Phase ordering or priorities?

5. **Timeline**: Do you want this done ASAP or phased over time?

---

**Once approved, I'll:**
1. Invoke plan mode on Copilot (Haiku) for Phases A, B, C, E
2. Invoke plan mode on Gemini for Phase D
3. Have all agents develop detailed implementation plans
4. Show you the combined plan before switching to execution mode

Ready to proceed?

---

**Plan Created**: 2026-02-16T20:10:00Z  
**Status**: ⏳ AWAITING USER APPROVAL  
**Next**: User reviews and confirms scope/approach/priorities
