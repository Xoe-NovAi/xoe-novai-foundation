# SPECIFICATION: Phase 4.1 - Service Integration Testing
**Status**: DRAFT
**Orchestrator**: Gemini 3 Flash
**Engineer**: Kimi K2.5 (Cline)
**Tactical Support**: Haiku 4.5 (Copilot)

## 1. Objective
Validate the end-to-end connectivity and stability of the Xoe-NovAi service ecosystem, including the Caddy Gateway, internal container DNS, and cross-service communication (REST, Redis, Postgres, WebSockets).

## 2. Requirements
- [ ] **Service Discovery**: All containers must resolve each other via internal Docker DNS.
- [ ] **Gateway Integrity**: Caddy must correctly route external requests to `rag_api`, `chainlit`, `vikunja`, and `mkdocs`.
- [ ] **Data Persistence**: Verify `rag_api` → `Redis` and `vikunja` → `Postgres` connectivity.
- [ ] **Streaming Validation**: Verify Server-Sent Events (SSE) and WebSocket stability for LLM responses.
- [ ] **Health Standardization**: Implement and verify `/health` endpoints for all services.

## 3. Constraints
- **Network**: All tests must run within the `xnai_network` or simulate bridge behavior.
- **Security**: Rootless Podman ONLY. No hardcoded credentials; use environment variables from `.env`. Zero-telemetry enforcement (no external API pings during test).
- **Hardware**: Testing must verify Ryzen/iGPU optimization (latency targets <200ms for health checks).
- **GPU Optimization**: Tests must verify Vega 8 / 64-wide wavefront occupancy for Vulkan-based health checks.
- **Memory Optimization**: Mandatory verification of 2-tier zRAM (lz4 + zstd) active state via `zramctl`.

## 4. Success Metrics
- [ ] 20+ pass/fail integration test cases.
- [ ] 100% reachability via Caddy Gateway.
- [ ] Zero OOM events during simulated load tests.
- [ ] Documentation updated in `internal_docs/03-infrastructure-ops/`.
- [ ] Audit passed for Ryzen 7 5700U / Vega 8 hardware alignment.
