XNAi Agent Bus — Agent Automation Hub Standardization

Name: XNAi Agent Bus (aka "XOH Agent Bus")

Purpose
- Standardize the multi-agent communication and automation hub so agents and new chat sessions can onboard instantly and operate securely and predictably.

Core requirements
- Backing store: Redis-backed agent state persistence (TTL, atomic updates) in addition to existing filesystem state for compatibility.
- Discovery: Consul service registration for agent discovery and health checks.
- Identity: Ed25519 handshake on agent registration; store public key fingerprint in data/iam_agents.db and Redis lookup.
- Concurrency: AnyIO TaskGroups for watchers and worker groups; provide a compatibility adapter for existing threaded agents until migration completes.
- Zero-telemetry: Default to local models (GGUF/ONNX/llama.cpp) and offline embeddings; any external API use must be explicitly flagged and audited.
- FRQ boosting: Carry frq_score metadata in messages and memory_bank entries; prioritize message queue processing using FRQ-aware priority queue.
- Resource awareness: Check /proc/meminfo and use conservative batch sizes (4-8) for embeddings on Ryzen 7 5700U; implement graceful eviction and model teardown patterns.
- Onboarding flow: agent -> registration endpoint -> Consul -> Ed25519 handshake -> persist public key & state -> mark agent active.

Deliverables
- Design doc and implementation plan (this file)
- Redis adapter module: scripts/agent_state_redis.py
- Consul registration helper: scripts/consul_registration.py
- Ed25519 identity module: scripts/identity_ed25519.py
- AnyIO migration adapter and rework of scripts/agent_watcher.py and scripts/agent_coordinator.py
- FRQ-aware priority queue & tests
- Unit and integration tests; CI checks; documentation for instant onboarding

Implementation order (recommended)
1. Redis adapter + state schema
2. Ed25519 identity registration flow
3. Consul registration + health checks
4. AnyIO TaskGroup migration (watchers -> tasks)
5. FRQ priority queue and message ordering
6. Tests, docs, PR

Notes
- Keep filesystem inbox/outbox/state compatibility for lightweight agents; prefer Redis for production orchestration.
- Use data/iam_agents.db to mirror identity fingerprints and for disaster recovery.
- Chosen canonical name: "XNAi Agent Bus" (alias: XOH Agent Bus).
