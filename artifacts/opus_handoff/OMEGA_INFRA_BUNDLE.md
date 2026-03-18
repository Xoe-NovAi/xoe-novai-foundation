# 🏗️ OMEGA BUNDLE 2: INFRASTRUCTURE & ARCHITECTURE (The Body)
**Target**: Opus 4.6 (Antigravity)
**Contents**:
1.  `SYSTEM_INFRASTRUCTURE_CONTEXT.md` (The State)
2.  `MULTI_CLI_ARCHITECTURE_GAPS.md` (The Gaps)
3.  `PODMAN_PYTHON_OPTIMIZATION.md` (The Hardening)
4.  `CRITICAL_SYSTEMS_AUDIT.md` (The Audit)

---
# FILE 1: SYSTEM_INFRASTRUCTURE_CONTEXT.md
# 🔱 Xoe-NovAi System Infrastructure & CLI Configuration Context
**Date**: Wednesday, March 18, 2026
**Identity**: Sovereign Omega (SESS-26 Hardened)
**Target**: Full system context for Claude.ai interaction.

---

## 1. System Overview
- **Codename**: Sovereign Omega
- **OS**: Linux (Ubuntu/Pop!_OS/Debian based)
- **Container Engine**: Podman (using `podman-compose`)
- **Primary Architecture**: Streaming-first, local-only, modular RAG stack.
- **Hardware Target**: CPU-optimized (AMD Ryzen 7 5700U / Zen2), 12GB RAM total limit (6GB allocated to stack).

---

## 2. Podman Infrastructure (Mesh)
The stack operates as a hardened mesh of 9 core services defined in `infra/docker/docker-compose.yml`.

### Core Services
| Service Name | Image | Role | Resources (Limit) |
| :--- | :--- | :--- | :--- |
| `xnai_consul` | `consul:1.15.4` | Service Discovery | 256M RAM, 0.2 CPU |
| `xnai_redis` | `redis:7.4.1` | Cache & Streams | 512M RAM, 0.5 CPU |
| `xnai_postgres` | `postgres:15` | Persistence (SQL) | 768M RAM, 1.0 CPU |
| `xnai_qdrant` | `qdrant:v1.13.1` | Vector Database | 1.0G RAM, 1.0 CPU |
| `xnai_rag_api` | `localhost/xnai-rag` | FastAPI Backend | 1.5G RAM, 2.0 CPU |
| `xnai_oikos` | `localhost/xnai-rag` | Mastermind/Orchestrator| 1.0G RAM, 1.0 CPU |
| `xnai_caddy` | `caddy:2.8-alpine` | Gateway (Ports 8000, 8005, 8006, 8012) | 256M RAM |
| `xnai_memory_bank_mcp`| `localhost/docker_m-b-mcp` | Gnostic Layer | 1.0G RAM |
| `xnai_library_curator`| `localhost/xnai-curator` | Ingestion Engine | 1.5G RAM |

### Networking & Volumes
- **Networks**: `xnai_db_network` (internal), `xnai_app_network` (gateway access).
- **Ports**:
  - `8000`: Caddy Gateway (Main Entry)
  - `8012`: RAG API (Internal: xnai_rag_api)
  - `8005`: Memory Bank MCP (Internal: xnai_memory_bank_mcp)
  - `8006`: Oikos Mastermind (Internal: xnai_oikos)
- **Persistent Storage**: `/library`, `/expert-knowledge`, `/storage/models`, `/storage/embeddings` (mapped from host media/omega_library).
- **UID/GID**: Services predominantly run as UID `1000`.

---
# FILE 2: MULTI_CLI_ARCHITECTURE_GAPS.md
# ⚠️ Multi-CLI Architecture Gaps

## 1. State Synchronization
-   **Gap**: Each CLI (Gemini, Cline) maintains its own memory/context.
-   **Fix**: **Agent Bus** (Redis Streams) + **Memory Bank MCP**. All agents must read/write to the MCP, not local files.

## 2. Tool Overlap
-   **Gap**: Both Gemini and Cline have "run_shell_command" tools.
-   **Fix**: Standardize on **Omega Tools** (MCP-based) so capabilities are identical.

## 3. Auth Management
-   **Gap**: Multiple `.env` files and token stores.
-   **Fix**: **OAuthManager** (Centralized Secret Store).

---
# FILE 3: PODMAN_PYTHON_OPTIMIZATION.md
# 🐍 Podman & Python Optimization (The 12GB Mandate)

## 1. Python Hardening
-   **Dockerfile**: Use `python:3.12-slim`.
-   **Dependencies**: Explicitly include `psutil` for memory monitoring.
-   **Garbage Collection**: Tune `gc.set_threshold()` for aggressive cleanup in low-RAM environments.

## 2. Podman Tuning
-   **Swap**: Disable swap for containers (`--memory-swap -1`) to force OOM and trigger restart policies (fail fast).
-   **Logging**: Use `json-file` with `max-size=10m` to prevent disk bloat.

## 3. zRAM Strategy
-   **Config**: 8GB size, `zstd` algorithm (high compression).
-   **Priority**: Higher than disk swap.

---
# FILE 4: CRITICAL_SYSTEMS_AUDIT.md
# 🚨 Critical Systems Audit (March 18, 2026)

## 1. Findings
-   **Port 8002 Conflict**: RAG API collided with Prometheus. **FIXED**: RAG moved to 8012.
-   **Missing psutil**: Base image lacked observability tools. **FIXED**: Added to Dockerfile.
-   **Consul Health**: Service discovery failing due to missing environment vars. **PENDING**: Need to inject `CONSUL_HOST`.

## 2. Recommendations
-   **Unified CLI**: Accelerate the OpenCode fork.
-   **Chaos Monkey**: Deploy to production (randomized testing).
