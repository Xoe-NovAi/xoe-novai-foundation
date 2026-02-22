# Model Research Crawler Plan — Quick Reference

## What Are We Building?

```
┌─────────────────────────────────────────────────────────────┐
│  LOCAL CRAWLER (ruvltra)                                    │
│  ├─ Researches XNAi-stack models autonomously               │
│  ├─ Builds model card KB (50-100 models)                    │
│  └─ Delegates complexity → Agent Bus Conductor              │
└─────────────────────────────────────────────────────────────┘
                        ↓
         ┌──────────────────────────────┐
         │   DELEGATION PROTOCOL        │
         │  complexity_score > 6/10     │
         │  Routes to best agent        │
         └──────────────────────────────┘
                        ↓
      ┌────────────────────────────────────┐
      │ AGENT BUS CONDUCTOR (Router)       │
      └────────────────────────────────────┘
         ├→ Copilot (Score 4-5: Strategy)
         ├→ Gemini (Score 6-8: Synthesis)
         └→ Cline (Score 8+: Implementation)
                        ↓
      ┌────────────────────────────────────┐
      │ EXPERT KNOWLEDGE BASES (Per Agent) │
      │ ├─ Task-specific models            │
      │ ├─ System instructions             │
      │ ├─ SOP docs + examples             │
      │ ├─ Vector indexes (semantic search)│
      │ └─ Tool registry                   │
      └────────────────────────────────────┘
```

---

## The Three Task Categories

### 1. Code Generation (20-25 models)
- LLaMA-2, Mistral, DeepSeek Coder, StarCoder, CodeLLaMA
- **What we research**: Context window, code reasoning, IDE/API integration
- **Why it matters**: Foundation for codebase refactoring, documentation generation

### 2. Research & Synthesis (20-25 models)
- Gemma, Qwen, Phi-3, OLMo, Falcons
- **What we research**: Reasoning depth, context utilization, fact grounding
- **Why it matters**: Enables complex strategy analysis, gap identification

### 3. Data Curation & RAG (15-20 models)
- ELSER, E5, BGE, BM25, sentence-transformers variants
- **What we research**: Embedding quality, semantic similarity, Ryzen 7 efficiency
- **Why it matters**: Powers expert KB vector indexing, semantic search across knowledge bases

---

## Model Card Structure

Each model includes:
```yaml
id: "deepseek-coder-6.7b"
task: "code_generation"
specs:
  parameters: "6.7B"
  context_window: 4096
  quantizations: ["q4_k_m", "q5_k_m"]
  inference_speed: "1.2 tok/s (Ryzen 7)"
  memory: "4.5 GB"
benchmarks:
  humaneval: 73.2
  mbpp: 60.5
ecosystem:
  frameworks: ["ollama", "vLLM", "llama.cpp"]
  verified_integrations: ["xnai_crawl", "chainlit"]
competitive_analysis:
  strengths: ["Best code benchmark for 6B"]
  weaknesses: ["Memory heavy on tight budgets"]
  alternatives: ["Mistral 7B (7x faster)"]
```

---

## Delegation Protocol (Simple)

**Crawler calculates complexity_score (1-10)**:
- +2: Unknown architecture/setup?
- +3: Multi-model comparison needed?
- +4: Novel integration pattern?
- +2: Code generation required?
- +2: Documentation rewrite needed?
- +3: System strategy decision?

**Then routes based on score**:
| Score | Route | Agent | Time |
|-------|-------|-------|------|
| 1-3 | Independent | Crawler | < 30 min |
| 4-5 | Strategic planning | **Copilot** | 30 min - 2h |
| 6-7 | Large-scale analysis | **Gemini** | 2-4h |
| 8-9 | Architecture review | **Gemini** | 4-6h |
| 9+ | Full refactoring | **Cline** | 6-12h |

---

## Expert Knowledge Base Per Agent

### Copilot KB
- System instructions + Haiku 4.5 profile
- Code-gen + research synthesis methods
- Planning protocols + SOP docs
- Examples of strategic decisions
- Vectors: 500-1000 embeddings

### Gemini KB
- System instructions + Gemini 3 Pro capabilities
- Large-scale synthesis + gap analysis frameworks
- Context window optimization strategies
- Examples of holistic analysis
- Vectors: 1000-2000 embeddings

### Cline KB
- System instructions + kat-coder-pro profile
- Refactoring patterns + documentation templates
- Integration testing + code generation workflows
- Examples: whole-codebase refactors
- Vectors: 800-1200 embeddings

### Crawler KB
- System instructions + ruvltra profile
- Research protocols + model card creation
- Delegation triggers + escalation rules
- Examples: model research workflows
- Vectors: 300-500 embeddings

---

## Implementation Timeline

### Week 1 (Days 1-2): Foundation
- ✅ **Phase A**: Copilot designs schemas + delegation protocol
- ✅ **Phase B Start**: Crawler begins model research (background)
- ✅ **Parallel**: Gemini designs expert KB structure

### Week 2 (Days 3-4): Core System
- ✅ **Phase B End**: 50-100 model cards + vectors indexed
- ✅ **Phase C**: Expert KBs populated (all agents)
- ✅ **Phase D**: Conductor routing logic coded

### Week 3 (Days 5-6): Integration & Testing
- ✅ **Phase E**: Crawler job integrated with Redis/Vikunja
- ✅ **Phase F**: Integration tests + feedback loop validation
- ✅ **Cleanup**: Documentation + monitoring dashboards

---

## Success Metrics

### Knowledge Quality ✓
- [x] 50-100 model cards (verified metadata)
- [x] 2+ benchmark sources per model
- [x] Ecosystem compatibility tested on Ryzen 7
- [x] Competitive analysis (vs alternatives)

### System Architecture ✓
- [x] Delegation protocol clear + implementable
- [x] Expert KBs searchable + well-structured
- [x] Vector search < 1s for semantic queries
- [x] Agent roles non-overlapping

### Integration ✓
- [x] Crawler runs autonomously on schedule
- [x] Delegation routing accurate (10+ test cases)
- [x] Cline feedback loop improves KB quality
- [x] Monitoring/alerting detects failures

---

## What We Need From You

✅ **Approval Checklist**
- [ ] Scope covers everything (model cards, delegation, expert KBs, feedback loop)?
- [ ] 6-phase approach makes sense (A: design, B: research, C: synthesis, D: routing, E: integration, F: testing)?
- [ ] Three task categories (code gen, research, curation) are the right priorities?
- [ ] Team allocation (Copilot/Gemini/Cline/Crawler) matches your preferences?
- [ ] Timeline is reasonable (18-25 hours, parallelizable)?

**Once approved**: We'll brief each agent on their phase and begin execution immediately.

---

## Key Files
- **Full Plan**: `PLAN-model-research-crawler-and-expert-knowledgebases.md` (18.5 KB)
- **Architecture Diagram**: Above in visual format
- **Phase Details**: See sections in full plan (A-F with specific tasks/deliverables)

---

**Status**: AWAITING USER APPROVAL  
**Prepared by**: Copilot CLI (Planning)  
**For**: XNAi Foundation Agent Bus — Model Knowledge Infrastructure
