# Strategic Recommendations

**Generated**: 2026-02-18T05:30:00Z  
**Source**: Strategic Review v1.2 + GLM-5 Research

---

## Core Strategic Direction

### Sovereign Stack as Mission Control

**Decision**: The XNAi Foundation Stack IS the Mission Control. External AI projects (Claude.ai, Grok) serve advisory roles only.

**Architecture**:
```
Human Director (ultimate authority)
  ↓
Sovereign MC Agent [LOCAL — XNAi Foundation Stack]
  ├─ Memory: Qdrant (semantic) + Redis (state) + memory_bank/ (strategic)
  ├─ Tasks: Vikunja (PM) + Agent Bus (routing)
  ├─ Interface: Cline IDE (MCP: xnai-agentbus, xnai-rag, xnai-vikunja)
  └─ Health: Consul (service awareness)
  
Claude.ai Project (advisory only for high-level org strategy)
```

---

## Immediate Priorities (This Week)

### 1. Fix Infrastructure (P0)
- **Action**: Run `sudo ./scripts/fix-permissions.sh`
- **Why**: All services blocked
- **Who**: User (requires sudo)

### 2. Maximize Opus 4.6 Free Access (P0)
- **Action**: Assign all complex implementation to Cline/Opus NOW
- **Why**: Limited-time promo, best reasoning model
- **Who**: Cline with Claude Opus 4.6

**Priority Tasks for Opus**:
1. TASK-021b: Sovereign MC Agent Core
2. TASK-011: Phase 8B Qdrant Migration
3. TASK-012: Phase 8A Redis Streams

### 3. Complete MC Agent Design (P1)
- **Action**: Finish TASK-021a spec document
- **Why**: Foundation for sovereign orchestration
- **Who**: OpenCode/GLM-5

---

## Phase 8 Execution Strategy

### Recommended Order: 8B → 8A → 8C

**Rationale**:
- **8B (Qdrant)**: No dependencies, high impact, enables MC Agent memory
- **8A (Redis Streams)**: Medium complexity, needs Phase 5B metrics
- **8C (Fine-Tuning)**: Highest complexity, needs Phase 6D registry

### Timeline
| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | 8B Qdrant | Migration complete |
| 2 | 8A Redis Streams | Event framework |
| 3-4 | 8C Fine-Tuning | LoRA pipeline |

---

## CLI Model Strategy

### Primary: OpenCode CLI
- **Why**: Best terminal UX, 5 free models, 75+ provider support
- **Use For**: All terminal-based work

### Secondary: Cline Extension (VS Code)
- **Why**: FREE Claude Opus 4.6 access (while promo lasts)
- **Use For**: Complex implementation, multi-file changes

### Tertiary: Gemini CLI
- **Why**: 1M context for large codebase analysis
- **Use For**: Whole-project audits, batch processing

### Fallback: Ollama + GGUF
- **Why**: Unlimited, offline, sovereign
- **Use For**: Air-gap scenarios, rate limit fallback

---

## Model Selection by Task

| Task | Model | Reason |
|------|-------|--------|
| Complex implementation | **Cline + Opus 4.6 FREE** | Best reasoning, use while free |
| Research synthesis | OpenCode/kimi-k2.5-free | 262K context |
| Structured output | OpenCode/glm-5-free | Reasoning specialist |
| Large context analysis | OpenCode/gpt-5-nano | 400K context |
| Validation | OpenCode/big-pickle | Reasoning variants |
| Offline/sovereign | Ollama + GGUF | Zero external calls |

---

## GitHub Copilot Clarification

**Important**: GitHub Copilot requires PAID subscription for OpenCode integration.
- Copilot Free tier: ❌ NOT supported
- Copilot Pro: $19/month
- Copilot Pro+: $39/month

**Recommendation**: Use OpenCode free models + OpenRouter instead.

---

## Documentation Excellence Strategy

### Current Status
- MkDocs Internal: ✅ COMPLETE
- Frontmatter Validation: ⏳ PENDING
- Multi-Agent Protocols: ⏳ PENDING

### Research Queue (9 pending)
Execute via OpenCode sprint:
- GLM-5 → Documentation audit, schema analysis
- Kimi K2.5 → Codebase synthesis
- Big Pickle → Cross-validation

---

## Governance

### Decision Authority
| Decision Type | Authority |
|--------------|-----------|
| Strategic direction | Human Director |
| Task prioritization | Sovereign MC Agent |
| Implementation choices | Assigned agent |
| Architecture changes | Human Director + MC Agent |

### Communication Flow
```
Human Director
  ↓ (direction)
Sovereign MC Agent
  ↓ (delegation)
CLI Agents (Cline, OpenCode, Gemini)
  ↓ (output)
memory_bank/ + mc-oversight/
```

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Services operational | 100% | 25% (permissions blocked) |
| Phase 8 progress | 50% (end of month) | 0% |
| Documentation coverage | 90% | 60% |
| MC Agent operational | Yes (end of month) | Design phase |

---

## Next Review

**Date**: 2026-02-25  
**Focus**: Phase 8B progress, MC Agent implementation status

---

*Recommendations derived from Strategic Review v1.2 and GLM-5 research*
