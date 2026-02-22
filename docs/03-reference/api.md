# API Reference

Auto-generated technical documentation for Xoe-NovAi core modules.

## Core APIs

| API | Description | Documentation |
|-----|-------------|---------------|
| **Main API** | RAG query, streaming, health | [main.md](api/main.md) |
| **Semantic Search** | Vector similarity search | [SEMANTIC_SEARCH_API.md](api/SEMANTIC_SEARCH_API.md) |
| **IAM Service** | Authentication & authorization | [iam_service.md](api/iam_service.md) |

## Worker APIs

| Service | Description | Documentation |
|---------|-------------|---------------|
| **Crawl Worker** | Library curation | [crawl.md](api/crawl.md) |
| **Voice Interface** | Chainlit voice UI | [voice_interface.md](api/voice_interface.md) |

## OpenAPI Schemas

Generated from FastAPI applications:

- [main_api.json](api/schemas/main_api.json)
- [semantic_search.json](api/schemas/semantic_search.json)

> **Note**: Run `python scripts/generate_openapi.py` to regenerate schemas.

## Error Codes

See [Error Handling](error-handling.md) for complete error reference.
