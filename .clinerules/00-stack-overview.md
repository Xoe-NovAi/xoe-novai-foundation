---
priority: critical
context: general
activation: always
last_updated: 2026-01-27
version: 1.0
---

# Xoe-NovAi Stack Overview & Philosophy

**Core Mission**: Democratize enterprise-grade local AI (RAG, voice-first, multi-agent) for anyone with basic hardware. Sovereign, offline-first, zero-telemetry, air-gapped capable.

**Golden Trifecta**:
1. Sovereign Data: LangChain + FAISS/Qdrant hybrid retrieval (BM25 + dense).
2. High-Performance Local Inference: GGUF quantized models (INT8/INT4 adaptive; AWQ not used due to GPU-only maturity and experimental CPU support).
3. Seamless UX: Voice-first (Piper TTS + Faster-Whisper STT), Chainlit interface, <300ms latency.

**Key Principles**:
- Torch-free everywhere (no PyTorch/Torch/Triton/CUDA/Sentence-Transformers).
- CPU + Vulkan only (Ryzen-optimized).
- Privacy-first: Zero external data transmission.
- Ethical Guardrails: Ma'at's 42 Ideals (truth, justice, compassion, sovereignty, wisdom).
- Evolution: Automatic research/gap analysis when capabilities are insufficient.
- Documentation: Torch-free MkDocs enterprise platform with Diátaxis structure, atomic migrations, strict validation.

**Performance Targets**: <500ms text / <300ms voice latency, <6GB RAM, atomic durability.

**Memory Bank Integration**: Reference memory_bank/projectbrief.md for mission alignment and memory_bank/systemPatterns.md for architectural consistency. Update memory_bank/activeContext.md after any architectural changes.

Always align suggestions with local-first, accessible, voice-guided democratization. Prioritize reversible changes with dry-runs and backups.
