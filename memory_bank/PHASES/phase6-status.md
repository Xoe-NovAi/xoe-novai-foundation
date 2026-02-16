# Phase 6: Observability & Vector Evolution
## Status: Active | Version: 1.0.0 | Date: 2026-02-15

### Critical Path
1.  **Vector Evolution**: Transition from FAISS-only to Tiered Hybrid (FAISS Shadow + Qdrant Full).
2.  **Infrastructure**: Prometheus/Grafana stack deployment.
3.  **Metrics**: Instrumentation of RAG API and Agent Bus.
4.  **Tracing**: OTel integration for multi-agent handoffs.

### New Artifacts
- `scripts/migrate_to_qdrant.py`: FAISS -> Qdrant orchestrator.
- `scripts/validate_qdrant_migration.py`: Pre-flight utility.
- `tests/test_qdrant_migration.py`: Migration test suite.
- `docs/QDRANT_MIGRATION.md`: Operational guide.
- `app/XNAi_rag_app/core/vector_cache.py`: Shadow Cache Manager (In Progress).

### Monitoring Strategy
| Component | Metric Source | Export Method |
|-----------|---------------|---------------|
| RAG API | FastAPI Instrumentator | Prometheus /metrics |
| Qdrant | Native | Prometheus /metrics |
| Redis | Redis Exporter | Prometheus |
| Agent Bus | Custom Heartbeats | Redis Streams -> JSON |
