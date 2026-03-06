# XNAi Agent Onboarding Checklist

**Version**: 1.0.0
**Purpose**: To provide a single, sequential guide for new agents to load project context. This document centralizes the established onboarding protocols found across the project.

---

## Onboarding Protocol

A new agent joining the XNAi ecosystem MUST follow these sequential steps to ensure full context and operational readiness.

### Phase 1: Minimal Context Load (The "Quick Start")

**Goal**: Achieve minimum required context to understand the project's mission and current status.

**Source**: `memory_bank/INDEX.md` ("For New Team Members")

**Action**: Read the following three core documents in order:

1.  `memory_bank/projectbrief.md` - Understand the project's mission, values, and constraints.
2.  `memory_bank/techContext.md` - Understand the technology stack and development environment.
3.  `memory_bank/activeContext.md` - Understand the immediate, most current work context and priorities.

### Phase 2: Session-Specific Tasking

**Goal**: Identify and understand the specific tasks assigned for the current session.

**Source**: `memory_bank/teamProtocols.md` ("Session Start Workflow")

**Action**: Read the latest `ACTIVE-TASK-DISPATCH-*.md` file found in the `memory_bank/strategies/` directory. Use the coordination key found in `activeContext.md` to identify the correct file.

### Phase 3: Session Handoff Review

**Goal**: Understand the immediate state of work left by the previously active agent.

**Source**: `memory_bank/recall/handovers/`

**Action**: List the contents of the `memory_bank/recall/handovers/` directory and read the most recent handover document. This provides critical, high-fidelity information about in-progress work, blockers, and recent discoveries.

### Phase 4: Deep Context Load (The "E5 Full Protocol")

**Goal**: Achieve a comprehensive, deep understanding of the entire XNAi ecosystem. This step is optional for simple tasks but **highly recommended** for Master Controller (MC) agents.

**Source**: `scripts/benchmark_runner.py` (`_generate_e5` function)

**Action**: Read the following 15 files that constitute the full onboarding protocol:

1.  `memory_bank/INDEX.md`
2.  `memory_bank/activeContext.md`
3.  `memory_bank/progress.md`
4.  `memory_bank/CONTEXT.md`
5.  `configs/agent-identity.yaml`
6.  `configs/model-router.yaml`
7.  `configs/free-providers-catalog.yaml`
8.  `.opencode/RULES.md`
9.  `memory_bank/teamProtocols.md`
10. `docs/architecture/XNAI-AGENT-TAXONOMY.md`
11. `memory_bank/ARCHITECTURE.md`
12. `expert-knowledge/esoteric/maat_ideals.md`
13. `expert-knowledge/origins/xoe-journey-v1.0.0.md`
14. `AGENTS.md`
15. `docs/DELEGATION-PROTOCOL-v1.md` (Self-added based on research)

---
## Post-Onboarding: Handling Evolving Context

Once onboarded, an agent must handle evolving context according to the established protocol.

**Action**: Adhere to the **"Memory Bank Update Protocol"** as defined in `memory_bank/teamProtocols.md`.
