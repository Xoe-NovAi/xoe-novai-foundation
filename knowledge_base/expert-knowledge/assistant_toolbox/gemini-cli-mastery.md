# Gemini CLI Mastery: Xoe-NovAi Edition
**Version**: 1.0.0 | **Expert**: Gemini CLI Agent

The Gemini CLI is the **Ground Truth Executor** of the Xoe-NovAi Foundation. With a 1M token context window and deep filesystem access, it is the ultimate tool for system-wide auditing and massive context ingestion.

---

## 🚀 Advanced Capabilities

### 1. Massive Context Auditing
Unlike models with smaller context windows, Gemini can ingest the entire `internal_docs/` and `memory_bank/` in a single pass. Use this for:
- Consistency checks across all documentation.
- Project-wide dependency mapping.
- Identifying "Dead Knowledge" (outdated docs).

### 2. Ground Truth Verification
Gemini CLI should be used to verify the outputs of other agents (Cline, Copilot, Claude).
- **Protocol**: If an agent proposes a file change, Gemini CLI should `read_file` the target and its surrounding context to ensure the proposal is grounded in reality.

### 3. Scribe Operations
Gemini CLI is the primary "Scribe" for the Memory Bank.
- **Task**: Updating `activeContext.md` and `progress.md` after major milestones.
- **Task**: Maintaining the `internal_docs/00-system/GENEALOGY.md`.

---

## 🛠️ Effective Patterns

### The "Parallel Search" Pattern
When investigating a bug, use multiple `grep_search` and `glob` calls in parallel to find all related symbols.

### The "Documentation Bridge" Pattern
Gemini CLI can bridge the gap between internal research (`internal_docs/02-research-lab/`) and public tutorials (`docs/02-tutorials/`).

---

## 📜 Key Commands for Gemini CLI
- `read_file`: Use with `limit` and `offset` for very large files.
- `run_shell_command`: Always explain the command first (Security Protocol).
- `list_directory`: Use recursively to understand nested structures.

---

**Expert Tip**: When in doubt, "Zoom Out". Use the 1M window to read the entire `memory_bank/` before making high-level strategic decisions.
