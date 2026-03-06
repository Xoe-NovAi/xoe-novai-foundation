# XNAi Architecture Overview (v4.0)

The XNAi Foundation v4.0 is built as a **Sovereign Multi-Agent Operating System**. It moves beyond standard RAG into a recursive, self-evolving intelligence stack optimized for local hardware (AMD Ryzen 5700U).

---

## 🏗️ Core Architecture

The stack is composed of five specialized layers that work in harmony to deliver high-confidence, sovereign research and implementation.

### 1. Unified Interface Layer
- **Open WebUI**: Consumer-grade chat interface for interacting with domain experts.
- **Chainlit**: Developer-focused voice and text UI for RAG experimentation.
- **Caddy Gateway**: Unified reverse proxy (Port 8000) providing secure, isolated access to all services.

### 2. Agentic Orchestration Layer (The "Brain")
- **Curation Manager**: Orchestrates the **Recursive Research (RRE)** loop.
- **Agent Memory 2.0**: PostgreSQL-backed state machine for persistent personas and "Shared Wisdom."
- **Agent Bus (Redis/Consul)**: Event-driven communication and service discovery.

### 3. Knowledge & Retrieval Layer
- **Hybrid Search**: Concurrent retrieval from **Qdrant** (Vector) and **LightRAG** (Knowledge Graph).
- **Corrective RAG (CRAG)**: Autonomous evaluation and query rewriting to ensure 95%+ data grounding.
- **Docling / Crawl4AI**: Advanced ingestion pipeline for technical manuals and deep web crawls.

### 4. Local Inference Layer (The "Engine")
- **Llama Server**: OpenAI-compatible API powered by `llama-cpp-python`, optimized for Zen 2.
- **OpenPipe**: Optimization layer for intelligent caching and model distillation.
- **Waterfall Escalation**: Automatic routing from SLM (0.6B) -> Krikri (8B) -> Cline (High-Reasoning).

### 5. Infrastructure Layer
- **PostgreSQL**: Reliable storage for Agent OS, Vikunja, and expert registries.
- **VictoriaMetrics / Grafana**: Real-time observability and health monitoring.
- **Podman/Docker**: rootless, isolated container orchestration.

---

## 🔄 The Self-Evolution Loop

1. **Request**: User asks a complex domain query.
2. **Recall**: Agent recalls "Shared Wisdom" from past successful tasks.
3. **Retrieve**: Parallel search across Vector and Graph databases.
4. **Evaluate**: Local SLM grades retrieval confidence.
5. **Research**: If confidence < 95%, the system autonomously crawls for new data.
6. **Evolve**: Agent publishes its "Lesson Learned" back to the shared wisdom repository.

---

## 🛡️ Sovereign Principles
- **100% Local**: No data ever leaves the Ryzen host (except optional Cline API calls for Level 3).
- **Maat Alignment**: Ethical guardrails (Truth, Balance, Order) baked into the core persona overlays.
- **Durable Identity**: Agent personas persist across sessions, remembering their unique perspectives and lessons.
