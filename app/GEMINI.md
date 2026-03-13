# 🚀 GEMINI.md: DOMAIN CONTEXT — /app [RIGID]

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

## 🔱 Phronetic Mandate (SESS-23)
1. **Gnostic Protocol Standard (GPS)**: All technical claims MUST reference an **Alethia-Pointer (AP)** to a **ZLV-verified** source.
2. **Crystal Rigidity**: Modifications to core logic (Linguistics, Auth, MCP) MUST maintain functional parity verified by **Crystal Hashing**.
3. **TGG Registration**: New imports or service dependencies MUST be registered in the **Topological Gnosis-Graph (TGG)**.
4. **Oikonomia Efficiency**: Agents must utilize **Parallel Tool Chains** as per the **STUP Master Protocol** to minimize token debt.

## 🎯 Domain Directives
1.  **AnyIO First**: Always use `anyio` (not raw `asyncio`).
2.  **Config First**: Use `CONFIG_PATH=/app/config.toml` (standardized across the mesh).
3.  **Port 8006**: RAG/Oikos API operates on Port 8006 (Caddy routes internally).
4.  **OAuth Protocol**: Use `OAuthManager` for decrypted credential handling (`XNAI_OAUTH_KEY`).
5.  **Rainbow Rotation**: Implement automatic account rotation upon 429/quota triggers.
6.  **Redis Standard**: `decode_responses=True` and `REDIS_SSL_CERT_REQS=none`.
7.  **Memory Guard**: LLM services MUST disable `mlock` (`LLAMA_CPP_USE_MLOCK=false`).

## 🛠 Tools & Commands
- `python -m pytest tests/ -x -q` — Run test suite
- `podman logs xnai_rag_api` — Check API state
- `curl http://localhost:8002/health` — Internal health check

## 🧠 Local Memory
Use `./.cli/` within this folder for domain-specific state.
- Metropolis Wiring: `docs/architecture/METROPOLIS_WIRING_MAP.md`
