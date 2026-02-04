# 🧠 The Living Brain Protocol: Expert Knowledge Standards

This document defines the strategy for populating and maintaining the `expert-knowledge/` base. This base is the shared "Long-Term Memory" for all Xoe-NovAi assistants, agents, and internal models.

## 🎯 Goal
To create a high-fidelity, evolving repository of technical mastery that enables AI agents to perform complex tasks with near-human accuracy and structural awareness.

---

## 🏗️ 1. Knowledge Structure (AI-Optimized)
All files in `expert-knowledge/` MUST follow the **Structured Semantic Format**:

### A. YAML Frontmatter
Used for metadata filtering in RAG systems.
```yaml
---
category: [coder|architect|security|tester|environment]
tags: [podman, uv, buildkit, rag, ryzen]
impact_level: [high|medium|low]
date_captured: 2026-01-24
related_components: [Dockerfile.base, Makefile]
---
```

### B. Hierarchical Markdown
Use Diátaxis-inspired headers to ensure the LLM understands the context.
- `# Title`: The Master Concept.
- `## Context`: Why this knowledge was captured.
- `## The Pattern`: The concrete implementation (code snippets).
- `## Edge Cases`: Known failure modes and pivots.
- `## Verification`: How to prove the pattern works.

---

## 📥 2. The Population Strategy
How we turn "hard-earned lessons" into permanent knowledge:

### I. The Research Synthesis
Whenever the **`stack-researcher`** completes a deep research task, it must summarize the findings into a new `.md` file in the appropriate sub-folder.

### II. The Post-Mortem Hook
Whenever the **`qa-specialist`** or **Gemini CLI** fixes a critical build blocker or bug:
1. Identify the "Root Cause."
2. Document the "Elite Fix."
3. Store in `expert-knowledge/coder/` or `tester/`.

### III. The Knowledge Loop
- **Step 1**: Agent encounters a problem.
- **Step 2**: Agent searches `expert-knowledge/`.
- **Step 3**: If found, execute the proven pattern.
- **Step 4**: If NOT found, perform research, solve, and **ADD THE PATTERN** to the base.

---

## 📂 3. Directory Mapping
- `_meta/`: Protocols, schemas, and indexing logic.
- `architect/`: System design, concurrency patterns, RAG logic.
- `coder/`: Language-specific mastery, build optimizations, library usage.
- `security/`: Rootless container hardening, zero-telemetry enforcement.
- `tester/`: Test suites, performance benchmarks, log analysis patterns.
- `environment/`: Hardware tuning (Ryzen), ZRAM, networking (pasta).

---
**Status**: 🟢 OPERATIONAL
**Mandate**: All Xoe-NovAi Agents MUST consult this base before execution.
