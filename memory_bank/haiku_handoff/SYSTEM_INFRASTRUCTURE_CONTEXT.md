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
- **Hardware Target**: CPU-optimized (AMD Ryzen 7 5700U / Zen2), 16GB RAM total limit (12GB Stack Cap).

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

## 3. Core Application Configuration (`app/config.toml`)
Detailed settings for the internal Python/FastAPI logic.

### Models & Performance
- **LLM**: `Qwen3-0.6B-Q6_K.gguf` (Context: 2048).
- **Embeddings**: `embeddinggemma-300m-Q6_K.gguf` (384 dimensions).
- **Threads**: 12 CPU threads (Zen2 optimized).
- **Memory Gating**:
  - Limit: 12.0 GB
  - Warning: 10.5 GB
  - Critical: 11.5 GB

### Redis Streams (The Agent Bus)
- **Coordination Stream**: `xnai_coordination`
- **Agent Bus**: `xnai:agent_bus`
- **Consumer Groups**: `agent_wavefront`, `memory_sync`, `alert_handlers`.

### Vector Store (Qdrant)
- **Collection**: `omega_library`
- **Distance Metric**: `cosine`

---

## 4. CLI & Service Bridge Integration
The system bridges standard CLI tools with the Omega Stack services via YAML configurations.

### CLI Bridge (`config_cli-service-bridge_prod_*.yaml`)
- **Integration Layer**: Handles task types like `RESEARCH`, `REASONING`, `EXECUTION`, `VALIDATION`.
- **Model Routing**: Dynamically routes between local LLMs (RAG) and external fallback providers (Rainbow Rotation).
- **Security**: Strict OAuth/API key handling through `OAuthManager`.

### Gemini CLI Integration (`config_gemini-cli_integration_*.yaml`)
- **Persona**: Jem (Synergy).
- **Protocol**: Gnostic Protocol Standard (GPS) / GPS Alethia-Pointers.
- **Lifecycle**: Research -> Strategy -> Execution (Iterative Plan-Act-Validate).

---

## 5. MCP (Model Context Protocol) Mesh
Available servers in `mcp-servers/`:
- `xnai-rag`: Direct RAG access.
- `xnai-gnosis`: Knowledge base / Alethia retrieval.
- `xnai-memory`: Short-term and long-term memory management.
- `xnai-stats-mcp`: Real-time system/resource monitoring.
- `xnai-agentbus`: Redis stream interface.
- `xnai-websearch`: Tavily/Serper integration.
- `xnai-github`, `xnai-vikunja`, `xnai-sambanova`.

---

## 7. Sovereign Observability & Resilience (Enterprise Standard)
The stack implements a hardened monitoring layer designed for offline, high-availability operations.

### **Health Monitoring (The 8-Pillar Check)**
The `healthcheck.py` script (v0.1.4) monitors 8 critical subsystems with circuit breaker integration:
1.  **LLM**: Verifies model path and context window loading.
2.  **Embeddings**: Confirms vector generation availability.
3.  **Memory**: Monitors the 10GB Operational Gate (Gatekeeper).
4.  **Redis**: Validates Stream and Cache connectivity.
5.  **Vectorstore**: Checks Qdrant collection health.
6.  **Ryzen**: Verifies CPU thread-pinning and Zen2 optimizations.
7.  **Crawler**: Validates CrawlModule v0.1.7 status.
8.  **Telemetry**: Enforces 8-point strict telemetry disablement.

### **Enterprise Logging (PII-Hardened)**
- **Format**: JSON (Structured) for automated log aggregation.
- **Security**: Automated SHA256 hashing for PII (Emails, IPs, SSNs, Credit Cards).
- **Performance**: High-resolution tracking for Token TPS, Query Latency, and Crawl Duration.

### **Resilience & Degraded Mode**
- **Circuit Breaker**: Services automatically enter "Degraded Mode" (local fallback) if external providers (Antigravity) fail.
- **Failover**: Multi-account "Rainbow Rotation" handles 429 errors seamlessly.

---
**Status**: ACTIVE
**Consistency Hash**: (Calculated at Runtime)
