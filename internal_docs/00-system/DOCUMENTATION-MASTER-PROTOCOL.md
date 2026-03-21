# DOCUMENTATION MASTER PROTOCOL: The "Omni-Scribe" Standard
**Version**: 1.0.0 | **Status**: ENFORCED | **Priority**: CRITICAL  
**Audience**: Gemini, Cline, Grok, Human Director

---

## 1. Core Philosophy
Documentation in the Xoe-NovAi Foundation is not merely a record; it is **Active Memory** for AI agents and **Strategic Intelligence** for humans. Every file must be structured for maximum machine-readability and high-context human synthesis.

## 2. Taxonomy Standard (The 00-07 Rule)
All internal documentation MUST reside within one of the eight numbered directories in `internal_docs/`. No files are permitted in the root of `internal_docs/`.

| ID | Category | Purpose |
| :--- | :--- | :--- |
| **00** | **System** | Infrastructure of knowledge: Strategy, Genealogy, Protocols. |
| **01** | **Planning** | Forward-looking intelligence: Roadmaps, PILLAR docs, Phase indices. |
| **02** | **Research** | Scientific and technical discovery: RESEARCH-P* reports, Sessions. |
| **03** | **Ops** | Deployment and stability: Infra audits, build logs, procedures. |
| **04** | **Quality** | Code integrity: Systematic audits, implementation manuals, reviews. |
| **05** | **Projects** | Applied knowledge: Client-specific implementations and templates. |
| **06** | **Team** | Human-AI collaboration: Onboarding, personas, handoffs. |
| **07** | **Archives** | Deep memory: Completed phases, legacy snapshots, archived roadmaps. |

## 3. Metadata Standard (Frontmatter)
Every new document MUST include YAML frontmatter to facilitate AI retrieval and tracking.

```yaml
---
last_updated: YYYY-MM-DD
status: [draft | active | complete | archived]
persona_focus: [Cline | Grok | Gemini | Human Director]
agent_impact: [low | medium | high | critical]
related_phases: [Phase-X]
---
```

## 4. AI-Readability Principles
To ensure AI agents can ingest and act on documentation without context drift:
1.  **Self-Containment**: Each document should explain its context or link directly to it.
2.  **Explicit Intent**: Use headers like `## Objectives` and `## Success Metrics`.
3.  **Standardized Naming**: Use the Unified Naming System (Cline, Grok, Gemini, Human Director).
4.  **Markdown Excellence**: Use Mermaid for diagrams and properly fenced code blocks.

## 5. Lifecycle Management
- **Drafting**: New findings are recorded in `02-Research` (Sessions).
- **Consolidation**: Validated findings are moved to `04-Quality` (Implementation Manuals).
- **Archiving**: Once a phase is 100% complete and its knowledge is integrated into the core stack, the transient phase documents move to `07-Archives`.

---

## 🛡️ Compliance & Enforcement
Gemini (Ground Truth Executor) is responsible for periodic "Freshness Audits" to detect taxonomy drift and ensure metadata compliance. Failure to adhere to these standards will result in a "Documentation Debt" alert in the `activeContext.md`.
