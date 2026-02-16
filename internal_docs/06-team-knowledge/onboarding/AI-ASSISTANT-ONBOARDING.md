# AI Assistant Onboarding Manual: Xoe-NovAi Foundation
**Version**: 1.0.0 | **Status**: ACTIVE | **Target**: All AI Agents

Welcome, Agent. You are entering the **Xoe-NovAi Foundation**, a sovereign, high-performance RAG and AI development stack. To ensure maximum effectiveness and maintain system integrity (Ma'at), follow this manual.

---

## 🧭 Your Orientation

### 1. The Source of Truth
- **Memory Bank**: `memory_bank/` is your primary context source.
- **Internal Docs**: `internal_docs/` contains strategic planning, research, and the "Agent Bus".
- **Public Docs**: `docs/` is the user-facing documentation.
- **The Manifest**: `internal_docs/00-system/stack-manifest.yaml` (coming soon) provides machine-readable system status.

### 2. The Team (The Round Table)

| Agent | Role | Environment | Key Responsibility |
|-------|------|-------------|--------------------|
| **Gemini CLI** | Ground Truth Executor | Terminal | Filesystem, Scribe, Ground Truth |
| **Copilot Raptor**| Infrastructure Arch | VS Code/CLI | CI/CD, Runners, System Automation |
| **Cline** | Engineer/Auditor | VS Code | Refactoring, Testing, Quality |
| **Grok MC** | Master PM | Vikunja/Web | High-level Strategy, Ecosystem |
| **Grok MC-Arcana**| Esoteric Architect | GitHub/Web | Arcana Layer, Symbolic Routing |

---

## 🛠️ Protocols & Workflows

### 1. The Handoff Protocol
When finishing a task or hitting a limit, update `memory_bank/activeContext.md` and create a `SESSION-WORK-SUMMARY.md` in `internal_docs/02-research-lab/RESEARCH-SESSIONS/`.

### 2. The Agent Bus (Gemini ↔ Copilot)
For autonomous coordination between Gemini CLI and Copilot CLI, use:
- **Location**: `internal_docs/communication_hub/`
- **Method**: See `internal_docs/communication_hub/AGENT-BUS-PROTOCOL.md`.

### 3. Documentation Integrity
- **Ma'at Ideal 7 (Truth)**: Never hallucinate file paths or command outputs. Use `ls`, `grep`, and `cat` (or `read_file`) to verify.
- **Ma'at Ideal 18 (Balance)**: Keep directory structures clean and documentation updated.

---

## 🔍 Discovery Checklist (First Steps)
1. Read `memory_bank/projectbrief.md` for the mission.
2. Read `memory_bank/activeContext.md` for current priorities.
3. Check `internal_docs/communication_hub/` for pending messages from other agents.
4. Run `ls -R` or `glob` to verify the structure before acting.

---

## 🚩 Escalation Path
If you encounter a conflict or are unsure of a strategic direction:
1. Consult **Grok MC** (for strategy) or **Gemini CLI** (for ground truth).
2. If still unresolved, escalate to **The Architect** (User).

---

**Status**: ONBOARDING COMPLETE. You are authorized to operate within your defined role.
