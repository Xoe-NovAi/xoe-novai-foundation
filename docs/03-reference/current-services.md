# Current Stack Services (March 2026)

**Last Updated**: 2026-03-01
**Purpose**: Reference for all active services in the XNAi Foundation Stack

---

## Active Services (20)

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| **consul** | consul:1.15.4 | 8500 | Service discovery & health monitoring |
| **redis** | redis:7.4.1 | 6379 | Cache, streams & Persistent Identity |
| **victoriametrics** | victoriametrics/victoria-metrics:latest | 8428 | Time-series metrics storage |
| **openpipe** | python:3.12-slim | 3000 | Sovereign LLM optimization layer |
| **qdrant** | qdrant/qdrant:v1.13.1 | 6333 | Vector database |
| **rag** | xnai-rag:latest | 8000 | FastAPI backend (RAG engine) |
| **ui** | xnai-ui:latest | 8001 | Chainlit Metropolis Interface |
| **knowledge_miner**| xnai-curation-worker:latest | - | Autonomous expert building |
| **crawler** | xnai-crawler:latest | - | Ingestion engine (standby) |
| **curation_worker** | xnai-curation-worker:latest | - | Knowledge refinement |
| **mkdocs** | xnai-mkdocs:latest | 8008 | Documentation server |
| **caddy** | caddy:2.8-alpine | 8000 | Unified reverse proxy |
| **open-webui** | ghcr.io/open-webui/open-webui:main | 8080 | Consumer Chat UI |

---

## Service Details

### Core Infrastructure

#### consul
- **Purpose**: Service discovery and health monitoring
- **Config**: Single server mode with UI
- **Data**: `/consul/data`

#### redis
- **Purpose**: Cache, session state, and message streams
- **Config**: Password-protected, 512MB limit, allkeys-lru eviction
- **Data**: `/data/redis`

#### victoriametrics
- **Purpose**: Time-series metrics (Prometheus replacement, 3-4x more efficient)
- **Config**: 365-day retention, 1GB limit
- **Data**: victoriametrics-data volume

#### qdrant
- **Purpose**: Vector database for semantic search
- **Config**: 1GB limit, gRPC enabled
- **Data**: `/qdrant/storage`

---

### Application Services

#### rag (FastAPI)
- **Purpose**: Main RAG engine with Qwen3-0.6B-Q6_K
- **Resources**: 4GB RAM, 2 CPU cores
- **Security**: Read-only filesystem, non-root user, no new privileges
- **Optimization**: Ryzen Zen 2 tuned (OPENBLAS_CORETYPE=ZEN, 6 threads)

#### ui (Chainlit)
- **Purpose**: Voice-enabled chat interface
- **Resources**: 2GB RAM, 1 CPU core
- **Voice**: Faster-Whisper STT + Piper TTS

#### crawler
- **Purpose**: Web content ingestion
- **Resources**: 2GB RAM, 1 CPU core
- **Status**: Standby (runs on-demand)

#### curation_worker
- **Purpose**: Knowledge refinement and entity extraction
- **Resources**: 1GB RAM, 0.5 CPU
- **Status**: On-demand (restarts on failure)

---

### User Interfaces

#### caddy (Reverse Proxy)
- **Purpose**: Unified entry point, TLS termination, rate limiting
- **Ports**: 8000 (public)
- **Config**: `/Caddyfile`

#### mkdocs
- **Purpose**: Internal documentation
- **Port**: 8008
- **Theme**: Material for MkDocs

#### booklore
- **Purpose**: Visual library manager for Books, Comics, Audiobooks
- **Port**: 8080 (via Caddy)
- **Volumes**: 
  - `library/sorted` → `/books`
  - `library/bookdrop` → `/bookdrop`

#### open-webui
- **Purpose**: Polished ChatGPT-like RAG interface
- **Port**: 8080 (via Caddy)
- **Integration**: Connects to llama_server for local inference

> ⚠️ This service uses an external GHCR image (~4 GB). See `docs/architecture/service-wiring.md` for guidance on replacing or trimming.

#### grafana
- **Purpose**: Observability dashboards
- **Port**: 3000
- **Data Source**: VictoriaMetrics (Prometheus-compatible)

---

### Project Management

#### vikunja
- **Purpose**: Task management and project hub
- **Port**: 3456
- **Database**: PostgreSQL (vikunja-db)
- **Cache**: Redis (db 5)

---

### AI Services

#### llama_server
- **Purpose**: Local LLM inference (OpenAI-compatible API)
- **Model**: Qwen3-0.6B-Q6_K.gguf
- **Context**: 32768 tokens
- **Resources**: 4GB RAM, 2 CPU cores

#### openpipe
- **Purpose**: LLM optimization (caching, deduplication, circuit breakers)
- **Port**: 3001
- **Sovereign Mode**: Zero telemetry enabled

#### cline
- **Purpose**: Sovereign CLI agent for autonomous tasks
- **Volume**: Workspace mount for full project access

---

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| Chat UI | http://localhost:8000 | Configured in .env |
| Library | http://localhost:8080 | Configured in .env |
| Vikunja | http://localhost:3456 | Configured in .env |
| Docs | http://localhost:8008 | None |
| Grafana | http://localhost:3000 | admin/admin |
| Consul | http://localhost:8500 | None |
| VictoriaMetrics | http://localhost:8428 | None |

---

## Configuration Files

| Service | Config Location |
|---------|-----------------|
| Stack | `docker-compose.yml` |
| App | `config.toml` |
| Caddy | `Caddyfile` |
| Redis | Environment variables |
| Models | `models/` directory |
| Library | `library/` directory |

---

## Recent Changes

### Added (Feb 2026)
- BookLore service
- Open WebUI service
- llama_server (local inference)
- KnowledgeMiner worker
- EntityRegistry for persistent personas

### Removed
- AWQ quantization (Feb 2026)

---

**Last Updated**: 2026-03-01
