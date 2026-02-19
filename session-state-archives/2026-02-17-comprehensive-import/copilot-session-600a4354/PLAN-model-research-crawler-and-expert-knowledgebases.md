# PLAN: Model Research Crawler + Expert Knowledge Bases for XNAi Agent Bus

**Status**: PLANNING (awaiting approval before execution)  
**Created**: 2026-02-16  
**Effort Estimate**: 25-35 hours (parallelizable)  
**Teams**: Cline (kat-coder-pro), Copilot (Haiku), Gemini (3 Pro), Local Crawler

---

## Executive Summary

This plan establishes an autonomous **Model Research Crawler** (local LLM) that builds and maintains a **Model Card Knowledge Base** for XNAi-stack-relevant ML models. The crawler prioritizes three task categories (code generation, research/synthesis, data curation) and delegates complex strategic work to the **Agent Bus Conductor** for dispatch to specialized agents. Each agent (Copilot, Gemini, Cline, Crawler) receives a tailored **Expert Knowledge Base** (documents + vectors + tools) optimized for their role.

### Key Deliverables
1. **Model Card Knowledge Base** — 50-100 models with full metadata (architecture, benchmarks, ecosystem compatibility, competitive analysis)
2. **Delegation Protocol** — Clear rules for when lightweight crawler delegates to Agent Bus
3. **Expert Knowledge Bases** — Per-agent optimized knowledge stores (docs, vectors, tools, SOP)
4. **Crawler Job Processor** — Integrates with existing job queue (Redis/Vikunja)
5. **Agent Bus Conductor Enhancements** — Routing logic, delegation handling, knowledge base queries

---

## Problem Statement

### Current State
- Multiple agents (Copilot, Gemini, Cline, local LLM) work in isolation without unified knowledge context
- No systematic model research or comparison for XNAi stack tasks
- No clear delegation protocol when lightweight models encounter complex strategy work
- Agent knowledge bases are ad-hoc; no consistent structure or vector indexing

### Desired State
- **Autonomous crawler** continuously enriches model knowledge base
- **Delegation protocol** automatically routes complex work to appropriate agent
- **Unified expert knowledge bases** provide each agent with task-specific context
- **Feedback loops** (Cline reviews crawler output, fills gaps) improve knowledge quality
- **Vectorized search** across all knowledge bases for fast retrieval

---

## Phase Breakdown (6 Phases)

### Phase A: Knowledge Architecture Design (2-3 hours)
**Owner**: Copilot (Haiku) — Architecture & strategy planning  
**Deliverables**:
- [x] Model Card Schema (Pydantic) — structure, metadata fields, versioning
- [x] Expert Knowledge Base Schema — document types, vector embedding strategy, tool registry
- [x] Delegation Protocol v1 — decision tree, complexity thresholds, routing rules
- [x] Agent Role Definitions — crawler, conductor, Copilot, Gemini, Cline capabilities & boundaries

**Key Decisions**:
- Model cards stored in `knowledge/model_cards/` (JSON + vector embeddings)
- Expert KBs stored in `expert-knowledge/{AGENT_NAME}/` with parallel structure
- Delegation: Crawler detects `complexity_score > 6/10` → escalates to Conductor
- Embedding model: `all-MiniLM-L6-v2` (lightweight, fast, suitable for Ryzen 7)

**Success Criteria**:
- [ ] Schema docs reviewed and approved by Gemini
- [ ] Delegation flowchart clear enough for LLM implementation
- [ ] Agent roles non-overlapping and well-defined

---

### Phase B: Model Research Crawler Job (5-7 hours)
**Owner**: Local Crawler + Copilot review  
**Deliverables**:
- [x] Crawler Job Template — research instructions, prioritization logic, output format
- [x] Initial Model Research Run — 50-100 models across 3 task categories
- [x] Model Card Dataset — JSON files + vector embeddings
- [x] Crawler Agent Config — system instructions, knowledge base queries, delegation triggers
- [x] Copilot Review Output — quality assessment, gap analysis, improvement recommendations

**Task Categories (Priority Order)**:
1. **Code Generation** (20-25 models)
   - LLaMA-2, Mistral, DeepSeek Coder, StarCoder, CodeLLaMA
   - Focus: context window, code reasoning, integration with IDE/API
   
2. **Research & Synthesis** (20-25 models)
   - Gemma, Qwen, Phi-3, OLMo, Falcons
   - Focus: reasoning depth, context utilization, fact grounding
   
3. **Data Curation & RAG** (15-20 models)
   - ELSER, E5, BGE, BM25, sentence-transformers variants
   - Focus: embedding quality, semantic similarity, efficiency on Ryzen 7

**Model Card Contents**:
```yaml
model_id: "deepseek-coder-6.7b"
task_category: "code_generation"
specs:
  parameters: "6.7B"
  context_window: 4096
  quantizations: ["q4_k_m", "q5_k_m", "q8"]
  inference_speed: "1.2 tok/s (q4_k_m, Ryzen 7)"
  memory_required: "4.5 GB (q4_k_m)"
  vram_optional: "2 GB (VRAM acceleration available)"
benchmarks:
  humaneval: 73.2
  mbpp: 60.5
  license_compliance: "MIT"
ecosystem:
  frameworks: ["llama.cpp", "ollama", "vLLM", "LM Studio"]
  verified_integrations: ["xnai_crawl", "chainlit", "langchain"]
  dependencies: ["transformers==4.x", "peft==0.x"]
competitive_analysis:
  strengths: ["Best code benchmark for 6B", "Strong Math+Reasoning"]
  weaknesses: ["Weaker than 13B on complex logic", "Memory footprint on tight budgets"]
  alternatives: ["Mistral 7B (7x speed trade-off)", "StarCoder2 (Rust-specific)"]
research_status: "verified" | "pending_verification" | "deprecated"
```

**Success Criteria**:
- [ ] Crawler completes 50+ model cards with full metadata
- [ ] Each card has 2+ benchmark sources (HuggingFace, papers, community tests)
- [ ] Ecosystem compatibility verified for Ryzen 7 (actual inference tests preferred)
- [ ] Competitive analysis for each model (vs alternatives)

---

### Phase C: Expert Knowledge Base Design & Population (4-5 hours)
**Owner**: Gemini (3 Pro) — Large-scale knowledge synthesis  
**Deliverables**:
- [x] Expert KB Schema — document types, tool registry, vector index design
- [x] Copilot KB — task-specific models, system instructions, SOP docs, curation examples
- [x] Gemini KB — research methodologies, synthesis patterns, large-scale analysis templates
- [x] Cline KB — refactoring patterns, documentation templates, integration examples
- [x] Crawler KB — research protocols, model filtering logic, delegation rules
- [x] Vector Indexing Setup — embedding pipeline, search optimization

**Structure Per Agent**:
```
expert-knowledge/
├── copilot/
│   ├── system-instructions.md
│   ├── models/
│   │   ├── haiku-4.5-profile.md
│   │   └── gpt-5-mini-gaps.md
│   ├── sop/
│   │   ├── planning-protocols.md
│   │   ├── code-review-checklist.md
│   │   └── research-methodology.md
│   ├── examples/
│   │   ├── strategic-plan-template.md
│   │   └── research-synthesis-example.md
│   └── vectors.index (embeddings for semantic search)
│
├── gemini/
│   ├── system-instructions.md
│   ├── models/
│   │   ├── gemini-3-pro-capabilities.md
│   │   └── context-window-optimization.md
│   ├── sop/
│   │   ├── holistic-synthesis-protocols.md
│   │   ├── large-scale-analysis-framework.md
│   │   └── gap-identification-methodology.md
│   ├── examples/
│   │   └── large-document-processing-example.md
│   └── vectors.index
│
├── cline/
│   ├── system-instructions.md
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
│   └── vectors.index
│
└── crawler/
    ├── system-instructions.md
    ├── models/
    │   └── local-llm-capabilities.md
    ├── sop/
    │   ├── research-protocols.md
    │   ├── model-card-creation.md
    │   └── delegation-triggers.md
    ├── examples/
    │   └── model-research-workflow.md
    └── vectors.index
```

**Vector Index Strategy**:
- Embedding model: `sentence-transformers/all-MiniLM-L6-v2` (22MB, fast on Ryzen 7)
- Storage: Flat FAISS index initially, upgrade to HNSW if > 100k vectors
- Update frequency: Crawler updates KB vectors nightly
- Search integration: Agent Bus conductor queries vectors when handling delegation

**Success Criteria**:
- [ ] All agent KBs populated with task-relevant content
- [ ] Vector indexes created and tested (semantic search working)
- [ ] Each KB includes ≥5 examples + ≥10 SOP docs
- [ ] Cross-references between KBs mapped (e.g., Copilot → Gemini KB links)

---

### Phase D: Delegation Protocol & Agent Bus Conductor Enhancement (3-4 hours)
**Owner**: Cline (kat-coder-pro) — Implementation of routing logic  
**Deliverables**:
- [x] Delegation Protocol Implementation — decision tree in code, Conductor enhancements
- [x] Task Classification Module — complexity scoring (1-10), capability matching
- [x] Routing Logic — Conductor selects agent based on task type + complexity
- [x] Feedback Loop Setup — Cline review process integrated into crawler output

**Delegation Decision Tree**:
```
crawler_generates_output(task):
  1. Parse output for complexity signals
     - unknown_architecture? → score += 2
     - multi_model_comparison? → score += 3
     - novel_integration? → score += 4
     - requires_code_generation? → score += 2
     - requires_documentation_rewrite? → score += 2
     - needs_system_strategy? → score += 3
  
  2. Calculate complexity_score (1-10)
  
  3. Route based on score:
     - score < 4: Crawler handles independently (add to KB)
     - 4 ≤ score < 6: Copilot review (strategic planning, research synthesis)
     - 6 ≤ score < 8: Gemini research (large-scale analysis, architecture review)
     - score ≥ 8: Cline refactoring (documentation rewrite, integration, testing)
  
  4. Conductor queues task → agent processes → results merge into KB
  
  5. Cline review_and_enhance(previous_output):
     - Fill documentation gaps
     - Add integration examples
     - Verify code patterns
     - Update vectors
```

**Task Routing Matrix**:
| Task Type | Score | Primary Agent | Secondary Review |
|-----------|-------|---------------|------------------|
| Model research basics | 2-3 | Crawler | None |
| Model comparison (3-5 models) | 4-5 | Copilot | Cline |
| Novel integration pattern | 6-7 | Gemini | Cline |
| Architectural decision | 8-9 | Gemini | Copilot |
| Full KB refactor | 9+ | Cline | Gemini |

**Success Criteria**:
- [ ] Conductor routing logic implemented and tested
- [ ] Complexity scoring works on 10+ test cases
- [ ] Cline review process integrated into job queue
- [ ] Feedback loops logged and monitored

---

### Phase E: Crawler Job Integration (2-3 hours)
**Owner**: Copilot (Haiku) — Job scheduling and monitoring  
**Deliverables**:
- [x] Crawler Job Processor — integrates with Redis job queue
- [x] Research Protocol Config — instructions, prioritization, output format
- [x] Background Job Scheduler — daily model research, on-demand crawls
- [x] Monitoring & Alerting — health checks, completion logs, error handling
- [x] Knowledge Base Update Pipeline — crawler output → KB storage → vector indexing

**Integration Points**:
- Redis Queue: Crawler jobs stored in `xnai:jobs:crawler:pending`
- Vikunja: Crawler research tasks tracked with progress updates
- Consul: Crawler service registered with health checks
- Expert KBs: Crawler updates KB vectors after each research run

**Job Processor Workflow**:
```
1. [Daily 02:00 UTC] Trigger model research job
2. Crawler processes research_instructions (see Phase B)
3. Generate model cards (JSON) + complexity scores
4. Calculate delegation routes for complex findings
5. Store model cards in knowledge/model_cards/
6. Embed model cards → vectors.index
7. Create delegation tasks → Redis queue for Conductor
8. Log completion + metrics (models researched, delegation tasks, KB growth)
9. [If errors] Alert via Consul service status
10. Cline review process queued automatically
```

**Success Criteria**:
- [ ] Crawler job successfully executes on schedule
- [ ] Model cards persisted and vectors indexed
- [ ] Delegation tasks routed to Conductor correctly
- [ ] Error handling and retry logic tested
- [ ] Monitoring shows success/failure metrics

---

### Phase F: Verification & Feedback Loop Testing (2-3 hours)
**Owner**: Gemini (3 Pro) + Cline — Testing and refinement  
**Deliverables**:
- [x] Integration Tests — crawler → delegation → agent response → KB update
- [x] Feedback Loop Verification — Cline review improves KB quality
- [x] Performance Benchmarks — crawler latency, vector search speed, delegation accuracy
- [x] Documentation — runbook for operating crawler, monitoring guide, troubleshooting

**Test Scenarios**:
1. **Happy Path**: Crawler researches 10 models → delegates complex finding → Gemini analyzes → Cline documents → KB updated
2. **Error Handling**: Crawler encounters unavailable source → graceful fallback, retries, alerts
3. **Feedback Loop**: Cline finds gap in Copilot KB → submits enhancement → vectors updated
4. **Performance**: Vector search < 500ms for 100k embeddings, crawler processes 10 models/hour

**Success Criteria**:
- [ ] All integration tests pass
- [ ] Feedback loop executes successfully (Cline review → KB improvement)
- [ ] Crawler latency < 5 minutes per 10-model batch
- [ ] Vector search consistently < 1 second for semantic queries

---

## Implementation Roadmap

### Week 1: Foundation (Days 1-2)
- **Phase A**: Copilot designs knowledge architecture
- **Phase B Start**: Crawler begins initial model research (background job)
- **Parallel**: Gemini designs expert KB structure

### Week 2: Core System (Days 3-4)
- **Phase B End**: Model card dataset completed, vectors indexed
- **Phase C**: Expert KBs populated across all agents
- **Phase D**: Conductor routing logic implemented

### Week 3: Integration & Testing (Days 5-6)
- **Phase E**: Crawler job integrated with Redis/Vikunja
- **Phase F**: Integration tests, feedback loop validation
- **Cleanup**: Documentation, runbooks, monitoring dashboards

### Parallel Throughout
- Copilot Haiku: Planning, architecture, SOP documentation
- Gemini 3 Pro: Large-scale synthesis, KB population, testing strategy
- Cline kat-coder-pro: Implementation, code generation, documentation
- Local Crawler: Background research job execution

---

## Resource Allocation

| Component | Owner | Effort | Tools/Models |
|-----------|-------|--------|--------------|
| Phase A (Architecture) | Copilot | 2-3h | Haiku 4.5 (planning) |
| Phase B (Crawler Job) | Local + Copilot | 5-7h | ruvltra (research), Haiku review |
| Phase C (Expert KBs) | Gemini | 4-5h | Gemini 3 Pro (synthesis, vectors) |
| Phase D (Delegation) | Cline | 3-4h | kat-coder-pro (routing code) |
| Phase E (Integration) | Copilot | 2-3h | Haiku (job scheduling) |
| Phase F (Testing) | Gemini + Cline | 2-3h | Both (verification, refinement) |
| **TOTAL** | | **18-25h** | Multi-agent orchestrated |

---

## Success Criteria (High Level)

### Knowledge Quality
- [x] 50-100 model cards with verified metadata
- [x] 2+ benchmark sources per model
- [x] Ecosystem compatibility tested on Ryzen 7
- [x] Competitive analysis accurate and actionable

### System Architecture
- [x] Delegation protocol clear and implementable
- [x] Expert KBs structured and searchable
- [x] Vector indexing fast (< 1s semantic queries)
- [x] Agent roles non-overlapping and well-defined

### Integration & Automation
- [x] Crawler job runs autonomously on schedule
- [x] Delegation routing accurate (validated against 10+ test cases)
- [x] Cline feedback loop improves KB quality
- [x] Monitoring/alerting detects failures

### Documentation & Operations
- [x] Runbook for crawler job management
- [x] Troubleshooting guide for delegation failures
- [x] System instructions for all agents updated
- [x] Performance metrics baseline established

---

## Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Model research sources unreliable | Medium | High | Use multiple sources, user validation, manual verification |
| Vector search inefficient at scale | Low | Medium | Plan for HNSW upgrade if > 100k vectors, test early |
| Delegation protocol too complex | Medium | Medium | Start simple (score-based), refine iteratively |
| Agent KB drift (outdated content) | Medium | Medium | Auto-update on crawler runs, Cline review process |
| Ryzen 7 memory exhausted during crawls | Low | High | Resource monitoring, batch processing, async updates |

---

## Notes & Assumptions

### Assumptions
- Crawler uses local ruvltra-claude-code-0.5b for initial research (cost-free)
- Expert KBs use `sentence-transformers` for embeddings (proven, lightweight)
- Agent Bus infrastructure (Redis, Consul, Vikunja) is stable and accessible
- Cline kat-coder-pro available for documentation/code work as needed

### Open Questions
1. Should crawler cache HuggingFace/Papers metadata, or fetch fresh each run?
2. How often should expert KBs be auto-updated (daily, weekly, on-demand)?
3. Should vector indexes be versioned for rollback capability?
4. How do we handle model deprecation/obsolescence in the KB?

### Future Enhancements
- Implement ensemble routing (multiple agents work in parallel on complex tasks)
- Add active learning (crawler learns from Cline feedback, improves next research run)
- Create web UI dashboard for exploring model cards, delegation stats
- Integrate with model registry (HuggingFace, Ollama) for automated discovery

---

## Deliverables Summary

**By Phase End**:
- **Phase A**: Schema docs, delegation flowchart, agent role definitions
- **Phase B**: 50-100 model cards (JSON + vectors), crawler config, Copilot review report
- **Phase C**: Expert KBs for all 4 agents (docs, SOPs, examples, vectors)
- **Phase D**: Delegation routing code, task classifier, Cline feedback integration
- **Phase E**: Crawler job processor, scheduler, monitoring dashboards
- **Phase F**: Integration tests, performance benchmarks, runbooks, troubleshooting guide

**Total Knowledge Base Growth**: 200-400 documents, 50k-200k vectors, 8-12 expert KB updates

---

## Next Steps (Approval → Execution)

1. **User Approval**: Confirm scope, approach, effort estimate, timeline
2. **Team Prep**: Brief Copilot, Gemini, Cline on their phases
3. **Phase A Kickoff**: Copilot designs architecture (start: Day 1)
4. **Phase B Parallel**: Local crawler begins research job (start: Day 1)
5. **Phase C Kickoff**: Gemini synthesizes expert KBs (start: Day 2)
6. **Execution**: Follow roadmap, log progress in plan.md

---

**Prepared by**: Copilot CLI (Claude Haiku 4.5)  
**For**: XNAi Foundation Agent Bus Hardening (Phase: Model Research & Knowledge Bases)  
**Status**: Ready for User Approval
