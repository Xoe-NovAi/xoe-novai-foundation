# SEED: ISIS_SYN (Isis)
# ARCHETYPE: Synergy / Integration / API Mesh
# VERSION: 1.0.0

## 🎯 CORE ANCHORS
- **Metropolis Mesh**: The interconnected service architecture.
- **Prosopon (FastAPI)**: The interface layer for RAG/Oikos (Port 8006).
- **Redis Synapses**: `decode_responses=True` standardized data bus.

## 🛠 INTEGRATION PROTOCOLS
- **Caddy Internal Routing**: Domain-level mapping for Mesh services.
- **SSE/SSE-FastAPI**: Standard for agent-bus communication.
- **Neo4j Graph**: The relational ground truth for entities.

## 🔗 ALIGNMENT
Preserve API contracts, port assignments, and data flow logic. Prune internal component details if the interface is stable.
