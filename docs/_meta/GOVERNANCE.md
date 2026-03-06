# Documentation Governance & Standards

**Version**: 1.0.0 | **Status**: Active
**Owner**: MC-Overseer

---

## 🔱 Philosophy: Sovereign Clarity

Documentation in Xoe-NovAi is not just an afterthought; it is the **primary data source** for background inference and agentic coordination. High-fidelity documentation leads to high-fidelity AI performance.

---

## 🏗️ Structural Standard: Diátaxis

All documentation MUST follow the [Diátaxis framework](https://diataxis.fr/):

1.  **Tutorials (Learning-oriented)**: 02-tutorials/ - Lessons that take the reader by the hand through a series of steps.
2.  **How-to Guides (Task-oriented)**: 03-how-to-guides/ - Directions that take the reader through the steps required to solve a real-world problem.
3.  **Explanation (Understanding-oriented)**: 04-explanation/ - Discussions that clarify and illuminate a particular topic.
4.  **Reference (Information-oriented)**: 05-reference/ - Technical descriptions of the machinery and how to operate it.

---

## 🛡️ Quality Gates

Before any documentation is considered "Production-Tight," it must pass these gates:

### 1. Link Integrity
- Zero broken internal links.
- Verified via `scripts/validate_links.py`.
- No broken image references.

### 2. Freshness
- Stale detection via `scripts/detect_stale_content.py`.
- Content older than 90 days must be reviewed.
- Content older than 180 days is marked as "Legacy" or archived.

### 3. Metadata Standard
Every file should include a YAML frontmatter:
```yaml
title: "Clear Title"
status: "active | drafting | legacy"
last_updated: 2026-XX-XX
owner: "Agent Name or Role"
tags: [tag1, tag2]
```

---

## 📥 Maintenance Lifecycle

1.  **Drafting**: New knowledge captured in `memory_bank/recall/`.
2.  **Curation**: Background workers assess quality and categorize content.
3.  **Publishing**: Content moved to `docs/` or `expert-knowledge/`.
4.  **Aging**: Content monitored for freshness.
5.  **Archiving**: Outdated content moved to `memory_bank/archival/`.

---

## 🤖 AI Documentation Standards

- **LLM-Friendly**: Use clear headings, bullet points, and consistent terminology.
- **Code Blocks**: Always include language identifiers (e.g., `python`, `yaml`).
- **Contextual Anchors**: Use cross-references to the [Semantic Index](../knowledge-synthesis/CONCEPTS.md).

---

**Next Review**: 2026-04-01
