# E5: Full XNAi Onboarding Protocol
# ====================================
# The model executes the complete XNAi Onboarding Protocol v1.0.0 as defined
# in the case study. This is the maximum-context environment.

## Setup Instructions

1. Start a fresh agent session
2. Pre-load the Phase 1 files (Core Context) into the context:

### Phase 1: Core Context (mandatory, ~14,000 tokens)
```
memory_bank/INDEX.md
memory_bank/activeContext.md
memory_bank/progress.md
memory_bank/activeContext/sprint-7-handover-2026-02-18.md
memory_bank/CONTEXT.md
```

3. Pre-load the Phase 2 files (Configuration Authority, ~12,000 tokens):
```
configs/agent-identity.yaml
configs/model-router.yaml
configs/free-providers-catalog.yaml
.opencode/RULES.md
```

4. Pre-load the Phase 3 files (Team & Architecture, ~8,000 tokens):
```
memory_bank/teamProtocols.md
docs/architecture/XNAI-AGENT-TAXONOMY.md
```

5. Pre-load the Phase 4 files (Deep Context, ~6,000 tokens):
```
memory_bank/PHASE-7-DEPLOYMENT-INTEGRATION.md
expert-knowledge/esoteric/maat_ideals.md
expert-knowledge/origins/xoe-journey-v1.0.0.md
expert-knowledge/research/OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md
```

6. Provide this prompt:

```
You have access to the XNAi Foundation project at:
/home/arcana-novai/Documents/xnai-foundation

I have loaded the complete XNAi Onboarding Protocol context for you.
Review all the loaded context carefully, then confirm your understanding.
I will ask you specific questions about the project.
```

7. Allow additional exploration if the model requests it
8. Run all 6 tests from test-battery.md

## What This Measures

The maximum achievable comprehension with full XNAi context engineering.
This is the **upper bound** — the best possible onboarding experience
the project's documentation architecture can provide.

The E5 score establishes:
- The ceiling for each model's performance on this project
- The XNAi Amplification Factor (XAF) when compared to E1
- The marginal value of the full protocol over the minimal pack (E5 - E4)

## Files Provided (15 files across 4 phases)

### Phase 1: Core Context
| File | Tokens | Content |
|------|--------|---------|
| `memory_bank/INDEX.md` | ~600 | Navigation map |
| `memory_bank/activeContext.md` | ~2,000 | Current sprint + taxonomy |
| `memory_bank/progress.md` | ~5,000 | Phase history + metrics |
| `sprint-7-handover-2026-02-18.md` | ~2,500 | Sprint deliverables + knowledge gaps |
| `memory_bank/CONTEXT.md` | ~4,500 | Tech stack + patterns + security |

### Phase 2: Configuration Authority
| File | Tokens | Content |
|------|--------|---------|
| `configs/agent-identity.yaml` | ~1,500 | Per-agent model/account registry |
| `configs/model-router.yaml` | ~6,000 | All providers, models, routing |
| `configs/free-providers-catalog.yaml` | ~5,000 | Free-tier provider catalog |
| `.opencode/RULES.md` | ~1,200 | 26 agent behavioral rules |

### Phase 3: Team & Architecture
| File | Tokens | Content |
|------|--------|---------|
| `memory_bank/teamProtocols.md` | ~5,500 | Agent roles, coordination, Vikunja |
| `XNAI-AGENT-TAXONOMY.md` | ~2,800 | Mermaid diagrams, routing decision tree |

### Phase 4: Deep Context
| File | Tokens | Content |
|------|--------|---------|
| `PHASE-7-DEPLOYMENT-INTEGRATION.md` | ~3,000 | Phase 7 completion details |
| `maat_ideals.md` | ~1,500 | 42 Ideals with architecture mappings |
| `xoe-journey-v1.0.0.md` | ~1,500 | Origin story |
| `OPUS-ONBOARDING-CASE-STUDY-2026-02-18.md` | ~8,000 | This benchmark's case study |

**Total context budget**: ~52,000 tokens pre-loaded (before model's own exploration)

## Expected Outcomes

- Frontier models (Opus, Gemini Pro): L5 (Architectural Intuition), scores 8-10 on all tests
- Strong models (Sonnet, DeepSeek-R1): L4-L5, scores 7-9 on T1-T4, 5-8 on T5-T6
- Mid-tier models (GPT-5 Mini, Kimi): L3-L4, scores 6-8 on T1-T3, 4-7 on T4-T6
- Free-tier models (big-pickle, GLM-5): L2-L3, scores 5-7 on T1-T2, 3-5 on T3-T6
- Local models (Qwen 7B): May not fit all 52K tokens in 32K window — truncated results expected

## Validation

After running all 6 tests, verify the model can answer YES to all 12 items
on the Validation Checklist (Section 6.2 of the case study document).
