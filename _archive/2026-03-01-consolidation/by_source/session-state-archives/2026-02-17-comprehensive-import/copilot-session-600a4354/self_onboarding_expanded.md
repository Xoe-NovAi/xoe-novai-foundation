Self-Onboarding — Detective Summary & Actionable Items

Purpose: Capture the key context extracted from the interrupted Copilot chat and provide a compact onboarding reference for future agent restarts.

Key findings
- Phase 5 validated and ready for execution; Phase 0 Extended audit recommended (2.7 hours) to consolidate overlapping docs.
- Core stack: Redis (decision persistence), Qdrant (semantic discovery), FAISS (local fallback).
- Critical pending items: user execution path choice (A/B/C) and Gemini CLI assignee.

Immediate actions (priority)
- [ ] Confirm execution path (A/B/C)
- [ ] Confirm Gemini CLI assignee (username or accept agent:gemini-cli)
- [ ] Approve Phase 0 Extended audit so Cline can begin batch audits
- [ ] Copilot: prepare batched Qdrant embedding scripts with memory-aware batching
- [ ] Cline: execute batch audits (6 batches), persist decisions in Redis
- [ ] Copilot: execute merges/archives, build FAISS backup, run mkdocs, validate links

Operational constraints
- Host memory: target peak <4.7GB on Ryzen 7 5700U; use zRAM and small embedding batches
- Zero-telemetry: no external API calls during embedding if not explicitly allowed
- Resilience: store audit decisions in Redis and create archived copies before merges

Where to find related docs
- internal_docs/01-strategic-planning/sessions/02_16_2026_phase5_operationalization/
- internal_docs/00-project-standards/COPILOT-CUSTOM-INSTRUCTIONS.md
- internal_docs/00-project-standards/REDIS-QDRANT-FAISS-BOOST-SYSTEM.md
- session-state/PHASE-0-EXTENDED-DOCUMENTATION-AUDIT-PLAN.md

Notes
- This file supplements memory_bank_onboarding.md and is designed to be read quickly by a new agent or human operator.
- Next step: if you approve, Copilot will (1) prepare embeddings, (2) create Vikunja tasks, and (3) hand off batches to Cline for review.
