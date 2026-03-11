# 🚀 GEMINI.md: DOMAIN CONTEXT — /app

**Domain**: `/app`
**Expertise**: FastAPI, Async Python (AnyIO), Redis Streams, Postgres, Qdrant
**Status**: ACTIVE | **Context Mastery**: 100% | **Sync**: v4.1.2

---

## 🚨 Active Audit Tasks in This Domain

| ID | Task | File | Status |
|:---|:-----|:-----|:-------|
| S1 | JWT signature verification | `app/XNAi_rag_app/core/token_validation.py` | SESS-02 NEXT |
| S4 | FAISS SHA256 gate | `app/XNAi_rag_app/core/dependencies.py` | NEXT |
| S5 | SanitizationResult Refactor | `app/XNAi_rag_app/core/security/sanitization.py` | NEXT |
| ST4 | `decode_responses` standardization | `dependencies.py` | IN PROGRESS |
| ST5 | `asyncio.get_event_loop()` fixes | `consul_client.py` | IN PROGRESS |

## 🎯 Domain Directives
1.  **AnyIO First**: Always use `anyio` (not raw `asyncio`).
2.  **Config First**: Use `CONFIG_PATH=/app/config.toml` (standardized across the mesh).
3.  **Port 8002**: RAG API operates on Port 8002 (Caddy handles traffic).
4.  **Redis Standard**: `decode_responses=True` and `REDIS_SSL_CERT_REQS=none` (Internal Mesh).
5.  **Memory Guard**: LLM services MUST disable `mlock` (`LLAMA_CPP_USE_MLOCK=false`) for rootless stability.
6.  **Standards Compliance**: Follow `docs/protocols/METROPOLIS_MESH_STANDARDS.md`.

## 🛠 Tools & Commands
- `python -m pytest tests/ -x -q` — Run test suite
- `podman logs xnai_rag_api` — Check API state
- `curl http://localhost:8002/health` — Internal health check

## 🧠 Local Memory
Use `./.cli/` within this folder for domain-specific state.
- Metropolis Wiring: `docs/architecture/METROPOLIS_WIRING_MAP.md`
