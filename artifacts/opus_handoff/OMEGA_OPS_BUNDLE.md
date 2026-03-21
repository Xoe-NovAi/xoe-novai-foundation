# ✋ OMEGA BUNDLE 3: OPERATIONAL PROTOCOLS & SPECS (The Hand)
**Target**: Opus 4.6 (Antigravity)
**Contents**:
1.  `MULTI_CLI_SESSION_MANAGEMENT.md` (Session Logic)
2.  `MULTI_CLI_SYSTEM_PROMPT_TEMPLATE.md` (The Prompt)
3.  `specs/BROWSER_MCP_SPEC.md` (New Spec)
4.  `specs/CHAOS_AGENT_SPEC.md` (New Spec)
5.  `specs/MAKEFILE_MODERNIZATION.md` (New Spec)
6.  `specs/GMC_WORKER_SPEC.md` (New Spec)

---
# FILE 1: MULTI_CLI_SESSION_MANAGEMENT.md
# 🕰️ Multi-CLI Session Management

## 1. Session Ledger
-   **File**: `SESSION_LEDGER.md`
-   **Format**: JSONL (Append Only).
-   **Fields**: `timestamp`, `agent`, `intent`, `outcome`, `files_changed`.

## 2. Handoff Protocol
-   **Pack**: When an agent finishes, it must generate a "Gnosis Pack" (summary + key files).
-   **Load**: The next agent reads the Pack to hydrate context.

---
# FILE 2: MULTI_CLI_SYSTEM_PROMPT_TEMPLATE.md
# 🤖 Multi-CLI System Prompt Template

## 1. Identity
You are **[AGENT_NAME]**, a specialized facet of the Omega Stack.
-   **Role**: [ROLE_DESCRIPTION]
-   **Hierarchy**: [LOGOS/PRAXIS/ARCHON]

## 2. Mandates
1.  **Gnostic Protocol**: Use Alethia-Pointers.
2.  **16GB Limit**: Respect the hardware.
3.  **Unified Tooling**: Prefer MCPs over ad-hoc scripts.

---
# FILE 3: specs/BROWSER_MCP_SPEC.md
# 🐼 OMEGA BROWSER MCP SPECIFICATION (Lightpanda Integration)
**Status**: DRAFT | **Target**: Opus 4.6 Implementation
**Role**: Autonomous Web Research & Interaction

## 1. Overview
The **Browser MCP** allows agents to browse the web safely and efficiently using **Lightpanda** (or a similar headless browser). Unlike simple `curl`, this supports JS rendering, navigation, and interaction, essential for "Deep Research" tasks.

## 2. Architecture
-   **Core Binary**: `lightpanda` (Go-based headless browser) or `playwright`.
-   **Interface**: MCP Tool (`browse_web`, `click_element`, `extract_text`).
-   **Security**: Runs in a sandboxed container (`xnai_browser`).

## 3. Tool Definitions

### `browse(url: str, query: str = None)`
-   **Description**: Navigates to a URL. If `query` is provided, it performs a search on the page or summarizes content relevant to the query.
-   **Output**: Markdown-formatted text of the page content.

### `screenshot(url: str, path: str)`
-   **Description**: Takes a screenshot for visual debugging or Vision model analysis.

## 4. Implementation Steps
1.  **Containerize**: Create `infra/docker/Dockerfile.browser` with Lightpanda/Playwright dependencies.
2.  **MCP Server**: Create `mcp-servers/xnai-browser/server.py`.
3.  **Agent Integration**: Add to `OMEGA_TOOLS.yaml` for Research Agents.

---
# FILE 4: specs/CHAOS_AGENT_SPEC.md
# 🐒 CHAOS AGENT SPECIFICATION (The Entropy Engine)
**Status**: DRAFT | **Target**: Opus 4.6 Implementation
**Role**: System Resilience Auditor

## 1. Overview
The **Chaos Agent** is a specialized background worker that intentionally introduces faults into the system to verify the resilience of the **Circuit Breakers** and **Self-Healing** mechanisms.

## 2. Directives (Rules of Engagement)
1.  **Never Kill State**: Never touch `xnai_postgres` or `xnai_qdrant` volumes.
2.  **Dev/Test Only**: Default to `dev` namespace. Require explicit override for `prod`.
3.  **Log Everything**: All actions must be logged to `logs/chaos_audit.jsonl`.

## 3. Capabilities (The Toolkit)

### `inject_latency(service: str, duration: int)`
-   **Effect**: Adds artificial delay to network packets (using `tc`).
-   **Goal**: Test Timeout Circuit Breakers.

### `kill_pod(service: str)`
-   **Effect**: `podman kill <service>`.
-   **Goal**: Test Restart Policies and Health Checks.

### `saturate_cpu(service: str, duration: int)`
-   **Effect**: Spikes CPU usage.
-   **Goal**: Test Resource Gating and "Turn-Based Queue" logic.

## 4. Implementation
-   **Script**: `scripts/chaos_monkey.py`.
-   **Schedule**: Controlled via **Oikos Mastermind** (not cron), triggered during "War Games" sessions.

---
# FILE 5: specs/MAKEFILE_MODERNIZATION.md
# 🛠️ MAKEFILE MODERNIZATION SPEC (Migration to `Just`)
**Status**: PROPOSED | **Target**: Opus 4.6 Refactor
**Goal**: Replace the brittle "God Makefile" with a modular Task Runner.

## 1. The Problem
The current `Makefile` is 2,200+ lines. It handles:
-   Docker orchestration
-   Python dependency management
-   Documentation building
-   Agent summoning
-   System monitoring

It is fragile, shell-dependent, and hard to read.

## 2. The Solution: `Just`
**Just** is a modern command runner. It supports:
-   **Cross-platform** (Linux/macOS/Windows).
-   **Language-agnostic** (Recipes can be Bash, Python, JS).
-   **Environment loading** (`.env` automatic).

## 3. Migration Strategy

### Phase 1: The Wrapper
Create a `Justfile` that wraps existing Make commands.
```just
# Justfile
default:
    @just --list

setup:
    make setup

up:
    make up
```

### Phase 2: modularization
Break the `Makefile` logic into `tasks/` scripts (Python/Bash) and call them directly from `Just`.

**Example Structure:**
```
root/
├── Justfile
├── tasks/
│   ├── docker.py
│   ├── agents.py
│   └── docs.py
```

### Phase 3: Deprecation
Remove `Makefile` once all commands are migrated.

## 4. Immediate Action for Opus
1.  Install `just`.
2.  Create the initial `Justfile`.
3.  Move complex logic (like "build-tracking") out of Make and into `scripts/setup/`.

---
# FILE 6: specs/GMC_WORKER_SPEC.md
# 🧹 GNOSTIC MEMORY CURATOR (GMC) WORKER SPEC
**Status**: DEFINED | **Target**: Immediate Implementation
**Role**: Hygiene & Curation

## 1. Overview
The **GMC Worker** is the "Janitor" of the Omega Stack. It ensures data hygiene, prevents "Backslash Bloat", and maintains the Chat Index.

## 2. Core Functions

### A. The "Backslash Stripper"
**Problem**: JSON serialization often double-escapes backslashes, leading to `\\\\\\\\n` bloat.
**Logic**:
```python
def clean_content(content: str) -> str:
    # Recursively reduce backslashes to single
    while "\\\\" in content:
        content = content.replace("\\\\", "\\")
    return content
```
**Trigger**: Pre-save hook on any `write_file` operation in the `memory_bank`.

### B. The Chat Indexer
**Goal**: Instant search of past sessions.
**Output**: `DISCOVERY_INDEX.md` (or JSON).
**Fields**:
-   `session_id`
-   `date`
-   `user_intent` (Summary)
-   `key_decisions` (List)
-   `files_modified` (List)

### C. The Pruner
**Logic**:
-   If `session_date` > 30 days AND `status` != "pinned":
    -   Move to `_archive/sessions/<year>/<month>/`.
-   Update Index to point to new location.

## 3. Implementation
-   **Script**: `scripts/gmc_worker.py`.
-   **Service**: Runs as a sidecar to `xnai_memory_bank_mcp`.
