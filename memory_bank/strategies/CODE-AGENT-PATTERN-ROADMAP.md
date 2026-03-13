# Code Agent Pattern & Implementation Roadmap

## Purpose
Provide a detailed strategy, roadmap, and resource catalogue for developing, deploying, and maintaining code agents in the XNAi Foundation stack (e.g., Cline, Gemini-MC, OpenCode connectors, etc.). This document will serve as a living guide for engineers and AI collaborators and will be referenced during Wave 4 closure and Wave 5 execution.

---

## 1. Guiding Principles

1. **Torch‑free & lightweight** – All agent code must avoid PyTorch/CUDA/Triton and instead rely on ONNX, GGUF, CTranslate2, or local runtimes. Models may be loaded via memory‑mapped GGUF or ONNX Runtime with Vulkan/CPU execution. Example: `app/XNAi_rag_app/services/voice/voice_module.py`.
2. **Zero‑telemetry / sovereignty** – No outbound telemetry. Use local logs and `CHAINLIT_NO_TELEMETRY=true` by default. Prefer file‑based storage and ensure all external requests are audit‑logged.
3. **Async/AnyIO first** – All IO must use `anyio` TaskGroups or async functions. Refactor existing asyncio violations; add tests to enforce. See `app/XNAi_rag_app/core/antigravity_dispatcher.py` for pattern.
4. **Configuration via environment** – Feature flags (e.g., `FEATURE_VOICE`, `FEATURE_QDRANT`) must control optional modules. Use pydantic `Settings` classes for type‑safe config.
5. **Circuit breakers & graceful degradation** – Wrap any network/RPC call with `pycircuitbreaker`. Fallbacks: Redis→in‑memory, Qdrant→FAISS→keyword. Agents must never crash due to provider failure.
6. **Memory‑bank integration** – Agents should load context using the `memory://` URI scheme and respect BLOCKS.yaml limits. Use `memory_replace`/`memory_append` for runtime updates.
7. **Feature‑flagged rollout** – New capabilities are gated behind environment variables and controlled via the agent bus (see `mcp-servers/xnai-agentbus`).
8. **Documentation‑first / patterns** – Each agent repository or module must include a README with the pattern, usage examples, and test coverage. Use Diátaxis classification.
9. **Testing and benchmarking** – Agents require unit, integration, and performance tests. Test batteries (see `benchmarks/test-battery.md`) ensure gap coverage and onboarding ability.

---

## 2. Roadmap

### Phase A: Foundation (Wave 4 Finalization)
- [x] Audit existing agents for principle compliance.
- [x] Add missing docstrings and READMEs (e.g. antigravity dispatcher, openpipe integration).
- [x] Add AnyIO TaskGroup wrappers around all async entrypoints.
- [x] Implement circuit breakers around external calls (licenses, provider APIs).
- [x] Establish core utilities: config loader, memory connectors, logging hooks.
- [x] Document pattern via this roadmap and add to `docs/03-how-to-guides/`.

### Phase B: Enhancement (Wave 5 Preparation)
- Build templates for new agents (cookiecutter repo) including scaffolding for pattern enforcement.
- Implement local model loader abstract class to unify GGUF/ONNX usage across agents.
- Publish a compliance checker script (`scripts/check_agent_compliance.py`) for env, imports, logging.
- Create a `agents/` directory under workspace with skeleton projects for new agents.

### Phase C: Extension (Wave 5 Execution)
- Develop Local Sovereignty Stack agents: offline model host, zRAM manager, air‑gap update daemon.
- Integrate code‑completion pipeline as plugin (deferred design from Wave 4 P2).
- Add community onboarding agent (Opus 4.6 review feedback) for local deployment.
- Iterate on performance benchmarks, tune memory footprint, and compile wave‑5 metrics.

---

## 3. Resources Required

### Documentation
- `docs/03-how-to-guides/agent-patterns.md` (new) – pattern summary
- `docs/architecture/` diagrams (agent taxonomy, bus flow)
- `memory_bank/strategies/CODE-AGENT-PATTERN-ROADMAP.md` (this file)
- Example modules: `app/XNAi_rag_app/core/antigravity_dispatcher.py`, `services/voice/voice_module.py`.

### Tools
- Compliance checker script (see Phase B)
- `pytest` plugins for async testing, `fakeredis`/`fakeqdrant` for mocks
- Circuit breaker library (`pycircuitbreaker`) with custom wrappers
- Onboarding benchmark packs (`benchmarks/context-packs/E5-full-protocol.md`)

### Knowledge bases
- Memory bank core blocks (`INDEX.md`, `systemPatterns.md`, etc.)
- Research reports on antigravity rotation, OpenPipe integration, voice orchestration
- Internal docs: `internal_docs/05-research/`, `internal_docs/04-code-quality/`

### Human resources
- Wave 4 engineers to finalize patterns
- Opus 4.6 (external reviewer) for pattern and roadmap feedback
- Documentation maintainer for continuous updates

---

## 4. Implementation Guides (Outline)
1. **Starting a new agent:** clone template → configure settings → implement core API methods → wrap with circuit breaker → add feature flags → write tests.
2. **Adding a provider:** extend `ProviderBase` class, register in `model-router.yaml`, add to `configs/free-providers-catalog.yaml`.
3. **Memory bank usage:** call `memory.load('memory://bank/<path>')`, respect TTLs, use `memory.append` to add logs.
4. **Testing:**  use `pytest.mark.asyncio` and `anyio` fixtures; run `pytest tests/agents/test_x.py`; measure with `benchmarks/agent-latency.yaml`.
5. **Deployment:** containerize as small image; include `ENTRYPOINT` script that loads environment and runs `python -m agent.main`.
6. **Onboarding:** ensure E5 pack passes; run `scripts/agent_onboarding_bench.sh` against new agent.

---

## 5. Monitoring & Maintenance
- Use Prometheus metrics exported via `observability.py`.
- Set up dashboards defined in `monitoring/agents.json`.
- Schedule monthly memory_bank review; add any new patterns to this guide.

---

## 6. Glossary
- **Agent**: autonomous Python service (Cline, Gemini-MC, etc.)
- **Provider**: external LLM or API used by an agent
- **Antigravity**: free-tier account scheduler
- **MC Overseer**: mission control monitoring service
- **E5 Onboarding**: maximum context onboarding protocol


*Document created 2026-02-25 and stored in memory_bank for Wave 4/5 reference.*