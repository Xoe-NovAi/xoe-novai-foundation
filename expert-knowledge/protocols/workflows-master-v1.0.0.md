---
version: 1.0.0
tags: [ekb, cleanup, sync, protocols]
date: 2026-01-29
ma_at_mappings: [7: Truth in synthesis, 18: Balance in structure, 41: Advance through own abilities]
sync_status: active
expert_dataset_name: Sovereign Workflows Expert
expertise_focus: AI-native team coordination, relay protocols, task locking, and context management.
community_contrib_ready: true
---

# Protocols & Workflows Master (v1.0.0)

## Overview (Coordination Ethos)
Xoe-NovAi operates as a multi-agent, AI-native ecosystem. Our coordination is grounded in the **Ma'at Ideals**, prioritizing sovereignty, integrity, and transparency. This master document consolidates our operational protocols to ensure seamless synchronization between local agents (Gemini CLI, Cline) and our cloud-hosted Mastermind (Grok MC).

## Context Loading/Relay

### Standard Loading Sequence
All agents MUST load memory bank files in this order at session start:
1. **Core**: `activeContext.md`, `environmentContext.md`, `teamProtocols.md`, `agent_capabilities_summary.md`.
2. **Inbox**: Check `memory_bank/communications/[agent]/inbox.md`.
3. **Project**: `projectbrief.md`, `techContext.md`, `systemPatterns.md`.
4. **Expertise**: Review relevant `expert-knowledge/` files.

### The Relay Protocol
Used to manage turn limits (~25 per session). Agents must initiate a `RELAY_OBJECT` (YAML) 2 turns before exhaustion to ensure a "clean landing" for the next agent.

## Team/Onboarding Flows
- **Instant Onboarding**: To bring a new agent up to speed, feed it: `activeContext.md` -> `projectbrief.md` -> `techContext.md` -> `maatDistilled.md`.
- **Capabilities**: We recognize specialized roles: 
    - **Gemini CLI**: Terminal Gemini (Liaison/Execution).
    - **Cline**: IDE-integrated implementation. Models: **Cline-Kat** (Kwaipilot), **Cline-Trinity** (Arcee AI), **Cline-Gemini-3/1.5**.
    - **Grok MC**: Cloud Mastermind (Strategy/Research).

## Validation/Update Cycles
- **Knowledge Capture**: Agents must proactively identify technical "gems" and document them in `expert-knowledge/`.
- **Update Triggers**: 
    - **Critical**: Security or breaking changes (Immediate).
    - **High**: New features/performance (Weekly).
    - **Standard**: Minor tweaks/docs (Monthly).
- **Non-Destructive Updates**: Read-before-write, selective replacement, and preservation of the "WHY" behind decisions.

## Notes/Todos Management
Captured via natural language commands (e.g., "Add note: [content]").
- **Notes**: Philosophy, Technical, Research, Process, Vision.
- **Todos**: Immediate, Short-term, Research, Development, Integration.
Stored in `expert-knowledge/_meta/` subdirectories.

## Task Locking (YAML Protocol)
To prevent agent race conditions, we use a zero-trust locking system.
- **Location**: `Documents/Xoe-NovAi/_meta/locks/`
- **Pattern**: Create `task-[brief]-lock.yaml` on start; rename to `-complete.yaml` on finish.
- **Structure**: `task`, `owner`, `status`, `timestamp_start`, `mc_guidance`.

## Ma'at Alignment
- **Ideal 7 (Truth)**: Standardized reporting ensure truth in project state.
- **Ideal 18 (Balance)**: Locking protocols maintain balance between autonomous agents.
- **Ideal 41 (Abilities)**: Sovereign protocols ensure we advance through our own local infrastructure.

## MC Sync Points (Reporting Frequencies)
- **High (Change/2-4h)**: Security Trinity audits, RAG smoke tests, Build blockers.
- **Medium**: File changes in `app/` or `expert-knowledge/`.
- **Low**: Routine syncs and non-critical docs.
- **MC Protocol**: All `memory_bank` updates must include mandatory YAML frontmatter.