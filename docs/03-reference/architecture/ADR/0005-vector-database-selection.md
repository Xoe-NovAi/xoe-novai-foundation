# ADR 0005: Vector Database Selection (FAISS + Qdrant)

## Status
Accepted

## Context
The XNAi Foundation Stack requires efficient vector similarity search for RAG (Retrieval-Augmented Generation) operations. We need a vector database that:
- Works offline with zero external dependencies
- Supports the target hardware (Ryzen 5700U, 8-16GB RAM)
- Provides low-latency retrieval (<100ms target)
- Supports hybrid search (BM25 + vector)

**Alternatives Considered:**

| Option | Pros | Cons |
|--------|------|------|
| **FAISS** (Meta) | Mature, CPU-optimized, no dependencies, proven | No persistence, single-node only, no filtering |
| **Qdrant** | Filtering, persistence, distributed mode, REST API | Higher memory, more complex |
| **Weaviate** | GraphQL, modules, hybrid | Heavy (Go), cloud-first design |
| **Pinecone** | Managed, performant | Cloud-only, not sovereign |
| **Chroma** | Simple Python API | Memory hungry, less mature |
| **Milvus** | Distributed, performant | Complex deployment, heavy |

## Decision
We adopt a **dual-mode approach**:

1. **FAISS** as the default/local vector store
   - Used for development and single-node deployments
   - Zero external dependencies
   - Optimal for 8-16GB RAM constraint
   - Integrated via `langchain-community`

2. **Qdrant** as optional enterprise backend
   - Enabled via `PHASE2_QDRANT_ENABLED=true`
   - Provides persistence and payload filtering
   - Supports distributed mode for scaling

**Migration Path**: Documented in `docs/QDRANT_MIGRATION.md`

## Consequences

### Positive
- **Sovereignty maintained**: Both options work fully offline
- **Flexibility**: Start simple (FAISS), scale later (Qdrant)
- **Performance**: FAISS provides <50ms retrieval on target hardware
- **Future-proof**: Qdrant supports distributed deployment

### Negative
- **Dual maintenance**: Must support both backends
- **Migration complexity**: Moving from FAISS to Qdrant requires data migration
- **Documentation overhead**: Must document both approaches

### Metrics (Post-Decision)
| Metric | FAISS | Qdrant |
|--------|-------|--------|
| Retrieval Latency | 35-50ms | 50-75ms |
| Memory (10k vectors) | ~200MB | ~350MB |
| Recall@10 | 92% | 95%+ |
| Persistence | No | Yes |

## Related
- `docs/QDRANT_MIGRATION.md`
- `config.toml` section `[rag]`
- `memory_bank/techContext.md`
