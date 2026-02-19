# Claude Opus 4.6 — Session Onboarding Brief
**Created By**: Cline (Claude Sonnet 4.5)  
**Date**: 2026-02-18  
**Purpose**: Bring Opus 4.6 fully up to speed for GLM-5 work review session  
**Platform**: VS Codium (Cline extension) — internet access enabled for research

---

## WHO YOU ARE IN THIS SESSION

You are **Claude Opus 4.6**, currently the most capable tool in the XNAi Foundation AI team. You are operating in the **Cline extension inside VS Codium**, which gives you:
- Full local filesystem access (`/home/arcana-novai/Documents/xnai-foundation/`)
- Internet research capability (confirm in VS Codium)
- MCP server access (if configured): xnai-agentbus, xnai-rag, xnai-vikunja

**Your role today**: Review work completed by OpenCode/GLM-5, validate findings, answer strategic questions, and advance implementation tasks.

---

## THE PROJECT: XNAi FOUNDATION

**What it is**: A sovereign, offline-first AI platform built for local hardware (Ryzen 7 5700U, 6.6GB RAM). Provides RAG, voice-first interface, and multi-agent orchestration. Zero external telemetry. Air-gap capable.

**Core stack**: Python 3.12, FastAPI, LangChain (torch-free), FAISS/Qdrant, Redis, Consul, Vikunja PM, Piper TTS, Faster-Whisper STT, Chainlit UI, Rootless Podman.

**Key constraint**: No PyTorch/CUDA/Triton/Sentence-Transformers. ONNX + GGUF + Vulkan only. AnyIO TaskGroups only (never asyncio.gather).

**Current branch**: `xnai-agent-bus/harden-infra` — 8 commits, some uncommitted files remain.

---

## CURRENT PROJECT STATE

**Phases 1–7**: ✅ COMPLETE  
- 119+ tests passing, Agent Bus production-ready, IAM v2.0, REST API, Voice interface, dual MkDocs documentation system

**Phase 8**: ⏳ STARTING  
- 8B: FAISS → Qdrant migration (first priority)
- 8A: Redis Streams integration (second)
- 8C: LoRA/QLoRA fine-tuning pipeline (third)

**Strategic pivot decided today (2026-02-18)**:  
The XNAi Foundation Stack itself is becoming the **Sovereign Mission Control** — using its own Qdrant (semantic memory), Vikunja (task management), Redis (state), Agent Bus (routing), and Consul (health) to self-direct. Claude.ai is reserved for high-level org advisory only. External Grok MC is retired.

---

## THE AI TEAM

| Agent | Role | Tool |
|-------|------|------|
| **Human Director** | Ultimate authority | N/A |
| **Claude Opus 4.6 (you)** | Primary implementer + reviewer | Cline in VS Codium |
| **OpenCode/GLM-5** | Research, structured analysis, gap reports | Terminal CLI |
| **OpenCode/Kimi K2.5** | Large-context synthesis (262k) | Terminal CLI |
| **Gemini CLI** | Whole-codebase 1M-context audit | Terminal |
| **Claude.ai Project** | Org-level strategy only (not daily) | Web |

**Free model note**: GitHub Copilot models via OpenCode require PAID subscription — confirmed by GLM-5 today. OpenCode's free pool = 5 native models. OpenRouter provides 31+ additional free models via API key.

---

## WHAT GLM-5 DID TODAY (Your Review Target)

GLM-5 completed three significant tasks. Your job is to review, validate, and extend this work:

### 1. Agent-CLI-Model Matrix v2.0.0
**File**: `expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md`  
**Review for**: Accuracy of model specs, correctness of task assignments, any gaps in coverage

### 2. OpenCode Comprehensive Guide v1.0.0
**File**: `expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md`  
**Review for**: Provider setup accuracy, RAG integration approach (MCP vs HTTP vs file), multi-agent orchestration patterns

### 3. Permissions Fix Script
**File**: `scripts/fix-permissions.sh`  
**Review for**: Correctness of UID 1001 ownership fix for Redis/Qdrant containers, safety, idempotency

### 4. Memory Bank Updates
**Files**: `memory_bank/activeContext.md`, `memory_bank/progress.md`  
**Review for**: Accuracy of current state, missing decisions from Feb 17–18 sessions

### 5. GLM-5's Questions for You (Answer These)
GLM-5 asked these in `mc-oversight/MESSAGE-FOR-OPUS-2026-02-18.md`:
1. Should we prioritize OpenRouter integration over HuggingFace? *(Answer: Yes — OpenRouter, clearly)*
2. Is the MCP server approach correct for RAG integration? *(Answer: Yes — already documented)*
3. Are there better model choices for specific XNAi tasks?
4. What tasks should be prioritized given free Opus 4.6 access?

*(Cline/Sonnet has already drafted answers in the strategic review — see Section 3.4. You may want to validate or extend these.)*

---

## KEY FILES TO READ FIRST

```bash
# 1. The master strategic review (your compass document)
cat internal_docs/00-system/STRATEGIC-REVIEW-CLINE-2026-02-18.md

# 2. GLM-5's handoff message to you
cat mc-oversight/MESSAGE-FOR-OPUS-2026-02-18.md

# 3. Current memory bank state
cat memory_bank/activeContext.md | head -80

# 4. What GLM-5 created
cat expert-knowledge/AGENT-CLI-MODEL-MATRIX-v2.0.0.md
cat expert-knowledge/OPENCODE-CLI-COMPREHENSIVE-GUIDE-v1.0.0.md
cat scripts/fix-permissions.sh
```

---

## YOUR IMMEDIATE PRIORITIES (In Order)

### Priority 1: Review GLM-5's Work (This Session)
- Validate the 3 new files for accuracy and completeness
- Correct any errors
- Answer GLM-5's 4 questions (or validate Cline's draft answers)

### Priority 2: TASK-005 — Fix Phase 3 Test Dependencies (Quick Win)
- Add `redis>=5.0.0` and `opentelemetry-exporter-prometheus` to requirements
- Run pytest to confirm Phase 3 test suite passes

### Priority 3: TASK-021b — Sovereign MC Agent Implementation (High Value)
- GLM-5 will write the spec (TASK-021a) — once available, you implement
- File: `app/XNAi_rag_app/core/sovereign_mc_agent.py`
- This is the architectural north star — the stack directing itself

### Priority 4: TASK-011 — Phase 8B Qdrant Migration (if time allows)
- Review `config/qdrant_config.yaml` and `docs/QDRANT_MIGRATION.md`
- Begin `scripts/migrate_faiss_to_qdrant.py`

---

## STRATEGIC CONTEXT: THE SOVEREIGN MC VISION

The XNAi Foundation was built sovereign from day one. The logical conclusion is that it should also *direct* itself. The Sovereign MC Agent is a local orchestration layer using:

- **Qdrant** for semantic memory of past decisions and project knowledge
- **Vikunja** for task tracking (REST API already available)
- **Redis** for session state and circuit breakers
- **Agent Bus** (Redis Streams) for routing work to CLI agents (you, GLM-5, Gemini)
- **Consul** for service health awareness
- **Memory Bank** (`memory_bank/*.md`) for strategic context

The three MCP servers already exist: `mcp-servers/xnai-agentbus/`, `mcp-servers/xnai-rag/`, `mcp-servers/xnai-vikunja/`. These make Cline IDE the natural interface for the Sovereign MC.

Claude.ai serves as an occasional high-level advisor for org-wide decisions — not a daily PM.

---

## USEFUL QUICK COMMANDS

```bash
# Project health
make up                                          # Start all services
docker ps --format "table {{.Names}}\t{{.Status}}"  # Check running containers
pytest tests/ -v --tb=short 2>&1 | tail -40      # Run tests
git log --oneline -10                            # Recent commits
git status --short | wc -l                       # Count uncommitted files

# Documentation
mkdocs build --clean                             # Public docs
mkdocs build -f mkdocs-internal.yml --clean      # Internal KB

# Service checks
redis-cli ping                                   # Redis
curl -s http://localhost:8500/v1/status/leader   # Consul
curl -s http://localhost:3456/api/v1/info        # Vikunja
curl -s http://localhost:8000/health             # FastAPI
```

---

## NOTES ON YOUR ENVIRONMENT

- **IDE**: VS Codium with Cline extension
- **OS**: Linux (Ryzen 7 5700U, 6.6GB RAM)
- **Internet**: Should be available for research in this session
- **Model context**: 200k tokens (not 1M — that was a documentation error)
- **Cost**: Currently FREE (limited-time promotion) — use for highest-complexity work

---

**You are ready. Start by reading the strategic review and GLM-5's message, then begin your review.**

*— Cline (Claude Sonnet 4.5), 2026-02-18*
