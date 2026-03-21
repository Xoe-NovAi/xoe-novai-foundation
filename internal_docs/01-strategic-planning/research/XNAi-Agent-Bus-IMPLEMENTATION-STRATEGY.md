XNAi Agent Bus Implementation Strategy (skeleton)

Objective
- Harden and operationalize the XNAi Agent Bus to provide fast, secure, and consistent onboarding for all agents and chat sessions.

Scope
- Redis state adapter with filesystem fallback, Consul service discovery and health, Ed25519 agent identity handshake, AnyIO-based watchers, FRQ-aware priority queueing, local model registry and model wrappers (GGUF support), and documentation + tests.

Knowledge gaps / research items
- Preferred local GGUF runtime on Ryzen 7 5700U (llama.cpp vs GGUF-native runners) and performance tuning (threads, 64-wide wavefronts for Vulkan where applicable).
- Embedding model choices for offline embeddings (EmbeddingGemma, SBERT variants) and batch sizes for memory constraints.
- Consul ACL & TLS requirements and how to secure service registration for multi-account workflows.
- Ed25519 key management best practices and safe storage patterns (data/iam_agents.db vs Redis-backed secrets store).
- AnyIO migration patterns for replacing threaded watchers without disrupting legacy agents.

Immediate implementation plan
1. Implement RedisAgentStateAdapter and ModelRegistry (skeletons added).
2. Implement Ed25519 identity module (skeleton added) and test key generation/signing locally.
3. Implement Consul registration helper (skeleton added) and provide sample registration flow.
4. Create AnyIO adapter and demonstrate a compatibility shim for existing threaded handler.
5. Validate ruvltra GGUF model locally and register in ModelRegistry; create a small wrapper to call the model runner.
6. Add FRQ-aware priority queue and tests.
7. Create onboarding docs and example agent registration flow.

Deliverables
- scripts/* skeletons (done), memory_bank model card (done), vikunja task (done), design docs (this file), test plan, and a PR with implementation + CI.

