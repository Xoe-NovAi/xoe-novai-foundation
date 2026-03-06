# Speculative & Escalation Research System (Omega-Stack)

## 🌌 Overview
The **Speculative & Escalation Research System** is a high-performance, hierarchical intelligence pipeline designed for resource-constrained environments (like the Ryzen 5700U). It combines **Speculative Embeddings** (Funneling) for retrieval and a **4-Level Escalation Chain** for reasoning.

## 🧬 Core Components

### 1. Speculative Embedding Engine (`speculative_engine.py`)
Optimizes vector search latency by progressively refining candidates through increasing dimensions:
- **Stage 1 (128d)**: Fast filtering of top 1000 candidates.
- **Stage 2 (768d)**: Semantic re-ranking of top 100.
- **Stage 3 (4096d)**: High-precision alignment of top 10.

### 2. Escalation Researcher (`escalation_researcher.py`)
A hierarchical research protocol that builds a **Research Dossier** as it scales:
- **Persistent Entities**: Each research turn is executed by a persistent persona (e.g., `philosophical_critic`) with its own **Procedural Memory**.
- **Continuous Learning**: Entities ingest feedback from every session via the `PerformanceFeedbackLoop`, allowing them to "remember" which strategies worked for specific query types.

## 🏙️ Agent Metropolis Architecture

The Omega Stack has evolved from a linear escalation chain into a **Metropolis of Persistent Experts**.

### 1. Persistent Intelligence Entities
Experts (Personas and Models) are no longer transient prompts. They are **Autonomous Identities** with:
- **Registry ID**: Unique identity in the `EntityRegistry`.
- **Procedural Memory**: A dedicated JSON store (`data/entities/`) tracking every interaction and lesson learned.
- **Domain Expertise**: Dynamic knowledge mapping to specific technical and creative domains.

### 2. Autonomous Knowledge Mining
When a new expert is summoned (e.g., "Kurt Cobain"), the system automatically:
1. Creates a new persistent identity.
2. Dispatches a mining task to the **KnowledgeMinerWorker**.
3. Performs deep research via **Crawl4AI** across role-specific sources (Gutenberg, arXiv, YouTube).
4. Injects findings into the **Gnosis Engine** and the expert's procedural memory.

### 3. Agent Summoning Tools
Agents can now autonomously consult experts using standardized tools:

#### `summon_expert(entity_name, query)`
- **Purpose**: Invoke an expert to provide a specialized perspective.
- **Behavior**: Retrieves the expert's procedural memory and applies their specific persona layer.

#### `compare_experts(entity1, entity2, topic)`
- **Purpose**: Triangulate truth by comparing different expert perspectives.
- **Example**: Compare "Socrates" and "Einstein" on the nature of reality.

---

## 🛠️ Implementation Details (v3.0)

### Registry & Persistence
- **File**: `app/XNAi_rag_app/core/entities/registry.py`
- **File**: `app/XNAi_rag_app/core/entities/persistent_entity.py`

### Interaction Patterns
Enhanced via `enhanced_handler.py`, supporting:
- **Hey {Entity}**: Direct summoning.
- **Ask {Entity} about {Query}**: Consultation.
- **Summon panel: {Entities}**: Multi-expert deliberation.
- **Hey {E1}, ask {E2} about {Query}**: Cross-entity communication.

## 📊 Surgical Metrics
To measure efficiency, the system tracks:
- **Confidence Velocity**: Δ Confidence / Δ Level.
- **Surgical Save Ratio**: Estimated tokens saved by targeted specialists vs. full escalation.


## 🤖 Agent Integration (How to use)

### Method A: Via Agent Bus (Standard)
Agents can dispatch a research task to the Redis-based Agent Bus:
```python
from XNAi_rag_app.core.agent_bus import AgentBusClient

client = AgentBusClient()
task_id = await client.dispatch_task(
    task_type="escalation_research",
    data={"query": "Your complex technical issue here"}
)
# The result will be posted back to the task_updates stream.
```

### Method B: Via CLI
```bash
python scripts/test_escalation_chain.py --query "How to optimize ZRAM on Linux?"
```

## 📦 Modularity & Portability
This system is designed as a **Standalone Service Layer**. To plug it into your own stack:
1.  **Redis Dependency**: Requires a Redis instance for the `Speculative Updates` stream.
2.  **Environment**: Ensure `llama.cpp` or a compatible inference server is running.
3.  **Config**: Update `config/escalation-config.yaml` with your model paths.

## 🧩 Knowledge Gaps & Future Work
- **Resource Contention**: Concurrent Level 4 (8B) requests may impact system latency. Implement a priority-based queue.
- **Multi-Modal Integration**: Currently restricted to text. Future versions will incorporate Vision for document OCR in the Level 3/4 dossiers.
- **Confidence Calibration**: Refine the math behind the "Confidence Score" using cross-model validation (Level 1 vs Level 4 agreement).

---
**Version**: 1.0.0 (Omega-Integration)
**Hardware Target**: Ryzen 5700U (8 Threads / 16GB RAM)
