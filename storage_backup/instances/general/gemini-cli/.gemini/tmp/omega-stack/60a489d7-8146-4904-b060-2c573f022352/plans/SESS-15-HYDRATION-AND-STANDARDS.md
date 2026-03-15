# 🔱 Implementation Plan: State Hydration & Engineering Standards Hardening

**Objective**: Formalize the "State Hydration Protocol" for agentic Memory Bank updates and ensure all new SESS-15 services (Librarian, Curation Bridge) meet Metropolis Foundation v4.1.2-HARDENED standards for observability, error handling, and `anyio` compliance.

---

## 📍 1. The State Hydration Protocol
**Goal**: Define a standardized workflow for agents to update the Memory Bank atomically.

### 📜 Protocol Definition (`docs/protocols/STATE_HYDRATION_PROTOCOL.md`)
- **Atomic Requirement**: Agents MUST update `INDEX.md`, `activeContext.md`, and `progress.md` in a single session "beat."
- **Verification Loop**: 
  1. Write updates to all three files.
  2. Perform a `grep` or `read` to verify the "Coordination Key" matches across all.
  3. Log the "Hydration Event" to `memory_bank/recall/handovers/`.
- **Hydration Template**:
  ```markdown
  ### 🌊 Hydration Event: [SESSION_ID]
  - **Status**: [STABLE/CRITICAL]
  - **Key Change**: [One sentence summary]
  - **Coordination Key**: [METROPOLIS-YYYYMMDD-STAMP]
  ```

### 🛠️ Agent Skill Implementation
- Create a reusable "State Hydrator" skill instruction for sub-agents (Facet-1, Generalist).

---

## 📍 2. Standards Hardening (Librarian & Bridge)
**Goal**: Audit and refactor new code for production-grade reliability.

### ⚡ AnyIO Compliance
- **Librarian**: Refactor `librarian.py` to use `anyio.run()` and `anyio.sleep()`.
- **Curation Bridge**: Ensure non-blocking polling loops using `anyio` task groups.

### 🩺 Healthchecks & Dashboards
- **Docker-Compose**: Add `healthcheck` block for `librarian` service (e.g., checking for process existence or Redis connection).
- **Grafana**: Add a "Librarian State" panel to the master dashboard (Tracking Compression Ratios and Queue Depth).
- **Error Handling**: Implement structured "Standard Exceptions" across all new worker services.

---

## 📚 Prerequisite Research
- [ ] **AnyIO Resource Cleanup**: Research `anyio.TaskGroup` for managing multiple background workers safely.
- [ ] **JSON Logging Standards**: Study `python-json-logger` for standardized Metropolis mesh logs.
- [ ] **Agentic Verifiers**: Research patterns for "self-verifying" file writes in LLM workflows.

---

## 🛠️ Implementation Steps

### Phase 1: Documentation & Skill Creation
- [ ] Create `docs/protocols/STATE_HYDRATION_PROTOCOL.md`.
- [ ] Create `.github/skills/state-hydrator.md` (if skills dir used) or update agent system prompts.

### Phase 2: Refinement of Services
- [ ] **Librarian**: Replace `asyncio` with `anyio`. Add `SIGTERM` handling for graceful shutdown.
- [ ] **Curation Bridge**: Implement exponential backoff for Vikunja polling failures.
- [ ] **Logging**: Standardize all logs to JSON format for better parsing by external collectors.

### Phase 3: Infrastructure Integration
- [ ] Update `infra/docker/docker-compose.yml` with the Librarian service definition and healthchecks.
- [ ] Update Grafana provisioned dashboards with new Librarian metrics.

---

## 🧪 Verification & Testing
- **Hydration Test**: Instruct a sub-agent to perform a dummy hydration and verify atomicity.
- **Resilience Test**: Simulate Redis failure and verify Librarian/Bridge graceful reconnection.
- **Performance Test**: Verify `anyio` overhead is negligible on Zen 2 hardware.
