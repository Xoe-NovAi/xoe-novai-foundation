# 🔱 Implementation Plan: GitHub Sync, MCP Expansion & Internal Directives Research

**Objective**: Secure the hardened Metropolis v4.1.2 state, synchronize with GitHub, integrate the Top 3 critical MCP servers, and research internal steering patterns for future optimization.

---

## 📍 1. GitHub & CI/CD Synchronization (Priority)
**Goal**: Push the current "Metropolis Hardened" state to the remote repository.

### 🛠️ Execution Steps
- [ ] **Stage & Commit**: Already complete on local `develop` branch.
- [ ] **Remote Push**: Execute `git push origin develop` (already complete).
- [ ] **Verification**: Confirm remote status and trigger CI/CD Stage 1-7.

---

## 📍 2. Critical MCP Expansion
**Goal**: Integrate the Top 3 most helpful MCP servers to eliminate context-switching.

### 🛠️ Top 3 Selection
1.  **Official GitHub MCP**: For autonomous PR reviews, Issue tracking, and cross-repo archaeology.
2.  **Exa / Brave Search**: For real-time, clean, LLM-ready documentation retrieval.
3.  **Official PostgreSQL MCP**: For direct, structured access to the IAM and Gnosis databases.

### 🏗️ Integration Path
- [ ] Research the configuration schema for each server in 2026.
- [ ] Update `.gemini/settings.json` with the new server definitions.
- [ ] Verify connectivity using a cross-server tool call test.

---

## 📍 3. Navigational Remediation & MkDocs
**Goal**: Ensure all strategy files are discoverable and indexed.

### 🛠️ Execution Steps
- [ ] **Master Index**: Update `docs/METROPOLIS_MASTER_INDEX.md`.
- [ ] **MkDocs Sync**: Align `mkdocs.yml` navigation with the new Master Index.

---

## 📍 4. SESS-20 Research: Internal Directives & Steering Patterns
**Goal**: Understand and utilize the "User Steering Update" and "Internal Instruction" patterns discovered during SESS-15.5.

### 🔍 Research Questions
- How are internal instructions generated from user steering?
- Can we "plant" intentional keywords in steering to guide complex multi-turn logic?
- Strategy for optimizing steering response latency.

---

## 🛠️ Implementation Phasing

### Phase A: Final Sync & Documentation
- [ ] Verify GitHub `develop` branch.
- [ ] Update README and Master Project Index (MPI).

### Phase B: MCP Integration
- [ ] Install and configure the 3 chosen MCP servers.
- [ ] Document the new toolset in `OMEGA_TOOLS.yaml`.

### Phase C: SESS-20 Initiation
- [ ] Conduct the deep-dive research into steering patterns.
- [ ] Propose a "Steering Mastery" protocol for future sessions.
