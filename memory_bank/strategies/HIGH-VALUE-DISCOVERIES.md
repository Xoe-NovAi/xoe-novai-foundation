# High‑Value Discoveries

This document collects significant insights uncovered during the deep repository audit, research runs, and strategic analysis performed on 2026‑02‑24 through 2026‑02‑25. These discoveries inform the code agent roadmap, Wave‑4 closure, and Wave‑5 preparation.

## Key Insights

1. **Memory Bank Hierarchy is Central** – Core/Recall/Archival structure with BLOCKS.yaml enforcement enables rapid onboarding and semantic search. The E5 onboarding protocol uses this to reach ~52k token context.
2. **Torch‑Free & Zero‑Telemetry Are Non‑Negotiable** – Repeated throughout docs, code, and CI. Any deviation is flagged as GAP-001 and can break project compliance measurements.
3. **Async/AnyIO Adoption Requires Clean‑Up** – 19 asyncio violations exist; migrating them will reduce deadlocks and align with agent behavior.
4. **Research‑First Workflow** – The project uses research jobs (RJ‑*) tracked in memory_bank with integration to Vikunja and OpenCode/GLM‑5. Nine pending requests highlight a backlog risk.
5. **Agent‑Bus & Antigravity Scheduler Hidden Complexity** – Antigravity dispatcher and agent‑bus coordination are critical for free‑tier rotation; they require dedicated test batteries and documentation.
6. **Documentation Gaps Are Strategic Blockers** – Gap‑009 and the empty `mc-oversight/` directory hinder new contributor onboarding and auditability.
7. **Wave‑4 to Wave‑5 Transition Defined** – Clearly articulated criteria and SOPs enable a smooth phase shift; the pattern roadmap document codifies best practices.
8. **Hand-off to External Models** – Creating explicit handoff docs ensures external reviewers (Opus 4.6) can participate in the project’s knowledge cycle.
9. **CI/CD for Docs & Code Under-Engineered** – No automated build for MkDocs or agents; this is a recurring manual step.
10. **Branch Strategy Missing** – Without it, contributions risk diverging; a simple Git flow is needed.

## Strategic Implications
- The code agent roadmap should be treated as a first‑class artifact and updated with each wave.
- Research jobs should be prioritized by risk (e.g., RJ‑014, RJ‑020) and executed by OpenCode/GLM‑5 to clear GAPs.
- Memory bank documents must be locked and referenced in progress reports to maintain accuracy.
- External collaboration (Opus, GLM‑5, Gemini) is successful when explicit handoff and onboarding protocols are provided.

*This file is intended to remain static; additions should be the result of new high‑value discoveries.*