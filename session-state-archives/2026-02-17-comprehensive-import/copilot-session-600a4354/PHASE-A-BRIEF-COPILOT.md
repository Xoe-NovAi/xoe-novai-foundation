# PHASE A BRIEF: Knowledge Architecture Design
## For: Copilot (Haiku 4.5) | Duration: 2-3 hours

**Status**: LOCKED & READY FOR EXECUTION  
**Owner**: Copilot CLI (Claude Haiku 4.5)  
**Approval Authority**: Cline (kat-coder-pro) ✅ APPROVED  
**Timeline**: Begin immediately; target completion within 3 hours  

---

## Your Mission (Phase A)

Design the foundational schemas, protocols, and architectural documentation for the entire Model Research Crawler system. Your work unblocks all other phases.

---

## Deliverables (4 files to create)

### 1. **`knowledge/schemas/model-card-schema.py`** (Pydantic)
**Purpose**: Define the structure for all model cards  
**Must include**:
- `id`: unique model identifier
- `task_category`: "code_generation" | "research_synthesis" | "data_curation"
- `specs`: parameters, context_window, quantizations, inference_speed_ryzen7, memory_required, vram_optional
- `benchmarks`: dict of benchmark_name → score (with sources)
- `ecosystem`: frameworks list, verified_integrations, dependencies
- `competitive_analysis`: strengths, weaknesses, alternatives
- `research_status`: "verified" | "pending_verification" | "deprecated"
- `vectors`: embedding_model_used, vector_index_location
- `metadata`: created_date, last_updated, researcher_notes, source_links

**Validation**: Must be importable, must validate example model card successfully  
**Example**: DeepSeek Coder 6.7B with all fields populated

---

### 2. **`knowledge/schemas/expert-kb-schema.py`** (Pydantic)
**Purpose**: Define structure for Expert Knowledge Bases  
**Must include**:
- `agent_name`: "copilot" | "gemini" | "cline" | "crawler"
- `documents`: list of KB documents (see Document schema)
- `vectors`: embeddings_model, vector_index_path, search_latency_sla_ms
- `tools`: list of tools/integrations available to this agent
- Document schema:
  - `id`: unique doc identifier
  - `title`, `content`, `document_type` (sop | example | system_instruction | reference)
  - `tags`: searchable categories
  - `version`: for tracking updates
  - `cross_references`: links to related docs in other agent KBs

**Validation**: Must support semantic search metadata (embedding ready)

---

### 3. **`docs/DELEGATION-PROTOCOL-v1.md`** (Flowchart + Pseudocode)
**Purpose**: Define how crawler detects complexity and routes to agents  
**Must include**:

#### Section A: Complexity Scoring Rubric
```
complexity_score = base_score (1-3)
if unknown_architecture: score += 2
if multi_model_comparison: score += 3  
if novel_integration: score += 4
if code_generation_required: score += 2
if documentation_rewrite_needed: score += 2
if system_strategy_decision: score += 3

# Task-specific modifiers
if task_category == "code_gen_research":
  score += 1  # Code gen has different complexity profile
if task_category == "rag_research":
  score += 0  # Baseline
```

#### Section B: Routing Decision Tree
```
if score <= 3:
  → Crawler handles independently (add to KB)
elif 4 <= score <= 5:
  → COPILOT (strategic planning, synthesis)
elif 6 <= score <= 7:
  → GEMINI (large-scale analysis)
elif 8 <= score <= 9:
  → CLINE (architecture review, refactoring)
else (score >= 9):
  → CLINE PRIORITY (full redesign)
```

#### Section C: Agent Capabilities Matrix
| Agent | Score Range | Expertise | Output Type | Turnaround |
|-------|---|---|---|---|
| Crawler | 1-3 | Research lookups, basic synthesis | JSON model cards | 10-30 min |
| Copilot | 4-5 | Strategic synthesis, comparisons | Markdown analysis | 30-120 min |
| Gemini | 6-8 | Large-scale analysis, architecture | Comprehensive reports | 2-4 hours |
| Cline | 8+ | Implementation, documentation, testing | Code + docs + tests | 4-12 hours |

#### Section D: Integration Points (Cline Feedback)
- **Crawler → Redis**: Job queued as `xnai:jobs:crawler:pending:` + complexity_score
- **Conductor routes**: Based on complexity_score, queues task for selected agent
- **Expert KB lookup**: Agent queries its KB via semantic search (<500ms SLA)
- **KB update**: Agent completes work → results stored in KB + vectors reindexed
- **Cline review**: Sampling-based (20% random + 100% high-complexity) → enhances KB

---

### 4. **`docs/AGENT-ROLE-DEFINITIONS.md`** (Detailed Role Specs)
**Purpose**: Crystal-clear role boundaries and capabilities  
**Must include**:

#### Crawler Role
- **Responsibility**: Research models, score complexity, delegate to Agent Bus
- **Inputs**: Research task (category, XNAi use case)
- **Outputs**: Model cards (JSON), complexity_score, delegation decision
- **Success criteria**: 6-8 models/hour, accurate complexity scoring, graceful error handling
- **Constraints**: No architecture decisions, no code generation, no documentation writing

#### Agent Bus Conductor Role
- **Responsibility**: Route tasks based on complexity_score, queue work, handle feedback
- **Inputs**: Task + complexity_score from Crawler
- **Outputs**: Task queued for appropriate agent, feedback summary
- **Success criteria**: Accurate routing (validated on 10+ test cases), no missed escalations
- **Constraints**: No analysis, no code generation, pure routing logic

#### Copilot Role (Haiku 4.5)
- **Responsibility**: Strategic synthesis, planning, code review, smaller-context research
- **Inputs**: Tasks with complexity 4-5 (strategic planning, synthesis)
- **Outputs**: Strategic analysis, planning documents, code reviews
- **Success criteria**: Quick turnaround (30-120 min), clear recommendations
- **Constraints**: Not for large-scale analysis (use Gemini), not for implementation (use Cline)

#### Gemini Role (3 Pro)
- **Responsibility**: Large-scale analysis, holistic synthesis, architecture review
- **Inputs**: Tasks with complexity 6-8 (novel patterns, architectural decisions)
- **Outputs**: Comprehensive analysis, architecture recommendations, gap identification
- **Success criteria**: Full context utilization (1M token window), actionable insights
- **Constraints**: Not for quick lookups (use Copilot), not for code implementation (use Cline)

#### Cline Role (kat-coder-pro)
- **Responsibility**: Implementation, documentation, testing, full refactoring
- **Inputs**: Tasks with complexity 8+ (implementation, refactoring, documentation)
- **Outputs**: Code + docs + tests, integration examples, KB enhancements
- **Success criteria**: Production-ready code, comprehensive documentation, verified tests
- **Constraints**: Not for strategy (use Gemini), not for quick research (use Copilot)

#### Non-Overlapping Verification
- ✅ Crawler: Research only (no synthesis, no code)
- ✅ Conductor: Routing only (no analysis, no implementation)
- ✅ Copilot: Strategy + review (no large-scale synthesis, no code)
- ✅ Gemini: Large-scale synthesis + architecture (no quick lookups, no implementation)
- ✅ Cline: Implementation + documentation (no strategy, no research)

---

## Success Criteria for Phase A

### Schemas Validation
- [ ] Both Pydantic schemas are syntactically correct (importable in Python)
- [ ] Model card schema validates example: DeepSeek Coder 6.7B card
- [ ] Expert KB schema validates example: Copilot KB structure

### Delegation Protocol
- [ ] Complexity scoring rubric is clear and code-ready
- [ ] Routing decision tree covers all score ranges (1-10)
- [ ] Integration points documented (Redis, Conductor, KB lookup, review)
- [ ] Validated against 5+ example tasks: complexity scores realistic

### Role Definitions
- [ ] All 5 roles clearly defined with responsibility, inputs, outputs
- [ ] Role boundaries non-overlapping (verified via checklist above)
- [ ] Success criteria measurable and specific
- [ ] Constraints documented (prevents cross-team work conflicts)

### Deliverables Quality
- [ ] Schemas are implementable by Cline in Phase D
- [ ] Delegation protocol is code-ready for task_classifier.py
- [ ] Role definitions are reference material for all agents

---

## Cline's Feedback for Phase A

From CLINE-REVIEW-FINDINGS.md, these clarifications should be reflected:

1. **Integration Points**: Document latencies and update strategy:
   - Expert KB semantic search: <500ms SLA
   - Vector reindex schedule: Nightly batch + on-demand triggers
   - Cline review → KB update: Git commit (history) + Redis update (performance)

2. **Delegation Complexity Sub-Categories**: Add modifier for "code_gen_research" vs. baseline

3. **Model Card Versioning**: Git tagging strategy:
   - Tag format: `kb-release-YYYY-MM-DD`
   - Include in schema: version field, source_links

4. **Crawler Error Handling**: Document fallback strategy (retries, fallback sources, escalation)

---

## How to Proceed

1. **Start immediately**: Create the 4 deliverables
2. **Validate locally**: Test Pydantic schemas with example data
3. **Quality gate**: Ensure all success criteria are met
4. **Return to Copilot CLI**: Share files + validation report
5. **Unblock Phases B, C, D**: Phase A completion unblocks all downstream work

---

## Resources Available

- **STRATEGY-CONSOLIDATED.md**: Full context on system architecture
- **CLINE-REVIEW-FINDINGS.md**: Knowledge gap research, integration clarifications
- **Previous Plans**: Reference documentation in session state

---

**Prepared by**: Copilot CLI  
**Status**: Ready to execute  
**Deadline**: Complete by Phase B start (next 3 hours target)
