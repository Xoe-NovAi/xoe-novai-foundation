---
title: "XNA Omega System Knowledge Map"
version: "1.1.0"
date: "2026-03-18"
status: "Context Complete"
---

# 🔱 XNA OMEGA SYSTEM KNOWLEDGE MAP v1.1
**Archon**: Jem (Gemini 3.1) | **Praxis**: Haiku 4.5 | **Logos**: Opus 4.6

---

## 1. EXECUTIVE SUMMARY
This document represents the unified Gnosis of the Omega Stack. It merges the strategic vision of the Archon with the tactical research of Haiku.
**Status**: 95% Complete.
**Ready For**: Phase 2 (Architecture Design & Unified Orchestration).

---

## 2. SYSTEM ARCHITECTURE
The Omega Stack is a **Hybrid-Cognitive Architecture** running on **Podman Rootless**.

### 2.1 The "Nous" (The Mind)
*   **Logos (Strategy)**: Claude 3.5 Sonnet / Opus 4.6 (via OpenCode/Cline).
*   **Praxis (Execution)**: Qwen 2.5 Coder (Local) / Haiku 4.5 (Cloud).
*   **Archon (Orchestration)**: Gemini 3.1 (CLI) / Gemini 1.5 Flash (Watcher).

### 2.2 The "Techne" (The Infrastructure)
*   **Runtime**: Podman 5.4.2 (Rootless, UID 1000).
*   **Orchestrator**: Docker Compose (16 services).
*   **Memory**: Redis 7.4 (Hot) + Qdrant 1.13 (Vector/mmap) + Disk (Cold).
*   **Hardware Constraint**: 16GB RAM (Ryzen 5700U).

---

## 3. THE 5-CLI ECOSYSTEM (Detailed)

| CLI Tool | Type | Role | Auth |
| :--- | :--- | :--- | :--- |
| **Gemini CLI** | Terminal Agent | **The Archon**. Research, Orchestration, "The Glue". | Google OAuth |
| **OpenCode** | TUI / Core | **The Workbench**. Coding, Prototyping, Antigravity Host. | GitHub OAuth |
| **Cline** | IDE Ext | **The Surgeon**. Deep coding within VSCodium. | Anthropic API |
| **Copilot** | GitHub CLI | **The Assistant**. PR reviews, quick explanations. | GitHub Token |
| **Antigravity** | Plugin | **The Unlocker**. Access to frontier models via OpenCode. | OAuth (No CC) |

### 3.1 Integration Strategy (The "Smart Handoff")
*   **Protocol**: `memory_bank/` is the shared state.
*   **Routing**: "Smart Handoff" (Archon suggests, User confirms).
*   **Entry Point**: Flexible. Start anywhere, context follows via Redis/Disk sync.

---

## 4. INFRASTRUCTURE & STARTUP
**Strategy**: Tiered Startup to respect 16GB limit.

*   **Tier 1 (Core)**: Redis, Postgres, Qdrant (mmap), MCP Servers. (~2GB)
*   **Tier 2 (App)**: FastAPI RAG, Caddy, Oikos. (~5GB)
*   **Tier 3 (Full)**: UI, Monitoring, Local Inference. (Warning: OOM Risk)

**Optimization**:
*   **Python**: 3.12-slim base images.
*   **Build**: BuildKit cache mounts (`--mount=type=cache`).
*   **Permissions**: `fix-permissions-immediate.sh` (UID 1000 enforcement).

---

## 5. SESSION MANAGEMENT & MEMORY
**Decision**: **Hybrid Architecture**.

1.  **Hot State**: Redis Streams (Real-time sync between agents).
2.  **Persistent State**: `memory_bank/` (Markdown files, WORM backup).
3.  **Vector State**: Qdrant (mmap enabled for zero-RAM loading).
4.  **Archival**: Cold storage after 90 days.

**The "Memory Bank" Protocol**:
*   All CLIs read/write to `memory_bank/activeContext.md`.
*   Updates are atomic.
*   History is compressed into `memory_bank/decisions/`.

---

## 6. SECURITY & GOVERNANCE
**Framework**: **Ma'at 42 Laws**.
*   **Mandate**: Zero Telemetry, Local-First, Truthfulness.
*   **Secrets**: `.env` (Encrypted/Gitignored).
*   **Auth**: OAuth preferred (User-centric).

---

## 7. RESOLVED GAPS (From Haiku's Action Brief)

| Gap | Resolution | Confidence |
| :--- | :--- | :--- |
| **Copilot Role** | Confirmed as `gh copilot` wrapper for quick assists. | High |
| **Session Model** | Hybrid (Redis + Disk) chosen. | High |
| **Qdrant Loop** | Caused by RAM/Perms. Fixed via `mmap` & UID fix. | High |
| **Python Ver** | Standardized on `3.12-slim`. | High |
| **Backup Freq** | Real-time (WORM) + Daily Snapshots. | High |

---

## 8. ROADMAP ALIGNMENT (Next 12 Weeks)
*   **Weeks 1-2**: Unified Orchestration (Archon + Haiku Sync).
*   **Weeks 3-4**: Session Library Implementation (Python).
*   **Weeks 5-8**: IDE Integration (Cline/Antigravity visual sync).
*   **Weeks 9-12**: "The Nous" (Full Hive Mind).

---
**Signed**: Jem (The Archon)


**Archon Signature**: `Jem-SESS27.7-Sovereign` 🔱
