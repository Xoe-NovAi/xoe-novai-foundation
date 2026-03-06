# API Reference

Auto-generated technical documentation for Xoe-NovAi core modules.

## Core APIs

| API | Description | Documentation |
|-----|-------------|---------------|
| **Main API** | RAG query, streaming, health | [main.md](../api/main.md) |
| **Multi-Provider Dispatcher** | Task routing & orchestration | [multi_provider_dispatcher.md](../api/multi_provider_dispatcher.md) |
| **Semantic Search** | Vector similarity search | [SEMANTIC_SEARCH_API.md](../api/SEMANTIC_SEARCH_API.md) |
| **IAM Service** | Authentication & authorization | [iam_service.md](../api/iam_service.md) |
| **Knowledge Access** | Secure document retrieval | [knowledge_access.md](../api/knowledge_access.md) |
| **Sanitization** | Content filtering and PII masking | [sanitization.md](../api/sanitization.md) |

## Infrastructure & Messaging

| Component | Description | Documentation |
|-----------|-------------|---------------|
| **Infrastructure Layer** | Core orchestrators and shims | [infrastructure-layer.md](../api/infrastructure-layer.md) |
| **Redis Streams** | Async agent bus coordination | [redis_streams.md](../api/redis_streams.md) |

## Worker & Interface APIs

| Service | Description | Documentation |
|---------|-------------|---------------|
| **Crawl Worker** | Library curation & discovery | [crawl.md](../api/crawl.md) |
| **Voice Interface** | Chainlit voice UI | [voice_interface.md](../api/voice_interface.md) |
| **Voice Module** | Low-level voice processing | [voice_module.md](../api/voice_module.md) |

## OpenAPI Schemas

Generated from FastAPI applications:

- [main_api.json](../api/schemas/main_api.json)
- [semantic_search.json](../api/schemas/semantic_search.json)

> **Note**: Run `python scripts/generate_openapi.py` to regenerate schemas.

## Error Codes

See [Error Handling](error-handling.md) for complete error reference.
