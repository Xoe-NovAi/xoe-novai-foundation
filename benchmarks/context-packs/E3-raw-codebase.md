# E3: Raw Codebase
# =================
# The model has full filesystem access but the memory_bank/ directory
# is EXCLUDED from exploration. This simulates a well-structured codebase
# without the XNAi context engineering layer.

## Setup Instructions

1. Start a fresh agent session
2. Provide this prompt:

```
You have access to the XNAi Foundation project at:
/home/arcana-novai/Documents/xnai-foundation

IMPORTANT: Do NOT read any files in the memory_bank/ directory.
Treat that directory as if it does not exist.

Analyze this project using only the source code, configs, docs, scripts,
tests, and infrastructure files. I will ask you specific questions about it.
```

3. If the model attempts to read memory_bank/ files, redirect it
4. Run all 6 tests from test-battery.md

## What This Measures

The value of code-level documentation (inline comments, docstrings, README,
configs, test files) WITHOUT the memory bank's strategic/historical/process layer.

This isolates the contribution of the memory bank specifically. The difference
between E3 and E5 scores represents the pure value of the memory bank architecture.

## Files Available (everything EXCEPT memory_bank/)

```
app/                   → Application code, Pydantic schemas, API endpoints
configs/               → agent-identity.yaml, model-router.yaml, free-providers-catalog.yaml
docs/                  → Architecture, tutorials, guides, references
internal_docs/         → Strategic planning, research lab, ops, quality
expert-knowledge/      → Research docs, model cards, protocols, esoteric, origins
.opencode/             → RULES.md, agents, commands, skills
.clinerules/           → Agent behavioral rules
.github/               → Workflows, instructions, skills
scripts/               → Signing, harvesting, agent watcher, health checks
tests/                 → Test suite
docker-compose.yml     → Infrastructure
Caddyfile              → Reverse proxy
Dockerfile*            → Container definitions
Makefile               → Build system
README.md, AGENTS.md, CONTRIBUTING.md
```

## Files EXCLUDED

```
memory_bank/           → ALL files (activeContext, progress, CONTEXT, handover, phases, protocols)
```

## Expected Outcomes

- Models should achieve L2-L3 from code exploration (services, configs, Docker)
- T4 (Strategic Assessment) will be significantly harder without progress.md and handover files
- T5 (Cross-Domain Synthesis) may still work partially via expert-knowledge/esoteric/
- T6 (Gap Identification) will miss phase-numbering and roadmap gaps (those live in memory_bank/)
- The E3→E5 delta quantifies the memory bank's contribution
