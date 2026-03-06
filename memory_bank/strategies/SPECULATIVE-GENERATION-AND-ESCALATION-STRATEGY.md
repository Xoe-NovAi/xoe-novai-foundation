# Speculative Generation & Escalation Strategy (v1.0)

**Project**: Omega Stack (Xoe-NovAi Foundation)
**Status**: DRAFT | **Priority**: CRITICAL
**Date**: 2026-02-28

---

## 🎯 Vision
Implement a high-efficiency retrieval and generation pipeline that leverages progressive refinement (funneling) and hierarchical model escalation to achieve >95% confidence in responses with minimal latency on Ryzen 5700U hardware.

---

## 🧬 1. Speculative Embeddings (The Funnel)

To optimize vector search, we implement a three-stage "Funnel" retrieval strategy:

### Stage 1: Fast Filter (128 Dimensions)
- **Model**: Light-weight projection or distilled model.
- **Goal**: High-speed initial candidate selection.
- **Operation**: Retrieve top 1000 candidates.

### Stage 2: Structural Refinement (768 Dimensions)
- **Model**: Standard transformer embedding (e.g., all-MiniLM-L6-v2).
- **Goal**: Re-rank Stage 1 candidates with better semantic understanding.
- **Operation**: Re-rank top 1000 to top 100.

### Stage 3: Deep Semantic Alignment (4096 Dimensions)
- **Model**: Large-scale embedding (e.g., Llama-3-8B level or specialized 4k model).
- **Goal**: Final high-precision retrieval.
- **Operation**: Re-rank top 100 to top 10.

---

## 🚀 2. 3x Researched Escalation Chain (Revised)

### Multi-Perspective Triangulation (The 3-Turn Persona Swap)
Each level performs 3 research turns. To ensure maximum accuracy, each turn employs a different **Expert Persona**:
1.  **Turn 1: The Skeptic (Adversarial)**: Specifically looks for contradictions and "dead-end" data in the RAG/Web results.
2.  **Turn 2: The Architect (Structural)**: Organizes findings into logical hierarchies and identifies missing dependencies.
3.  **Turn 3: The Synthesizer (Holistic)**: Merges the findings into the current Dossier with a focus on user intent.

### Dynamic Model Selection
The `ThinkingModelRouter` dynamically selects the model for each level based on:
- **Query Domain**: (e.g., Code -> `deepseek-coder`, Creative -> `haiku`).
- **Hardware Load**: Shifts to lighter models if Ryzen 5700U thermal/RAM pressure is high.
- **SLA Requirements**: Prioritizes speed or depth based on the task priority.

### 🎯 Targeted Follow-up ("Hey [Model]...")
The system maintains a **Chain Context Map**. If a user types "Hey Tiny..." or "Hey Krikri...", the system re-invokes that specific model using its unique contribution to the Dossier as the primary context.

---

## 📊 4. Metrics & Observability (The Study Lab)

We utilize established Omega Stack services to study performance:
- **VictoriaMetrics**: Tracks `latency_per_level`, `token_efficiency`, and `confidence_velocity`.
- **Redis Streams**: Real-time observability of the internal "Model Dialogue".
- **Agent Bus**: Allows Level 4 to "request a peer review" from another 8B model if confidence is borderline.


---

## 🛠 4. Infrastructure Requirements

1.  **Redis Streams**: `xnai:agent_bus` for coordination and `xnai:speculative_updates` for real-time UI.
2.  **Llama-Server**: Configured with `--draft-model` and `--draft-max` as per `heavy_lift_turbo.sh`.
3.  **Vector Store**: Qdrant/FAISS configured with multi-dimensional indexing.
4.  **Hardware Offload**: Vulkan/Ryzen 5700U optimized (8 threads, mmap).

---

## 📋 Implementation Roadmap

1.  **Step 1**: Implement `SpeculativeEmbeddingEngine` in Python.
2.  **Step 2**: Update `ThinkingModelRouter` to support the 4-level escalation logic.
3.  **Step 3**: Integrate real-time Redis updates in `chainlit_app_unified.py`.
4.  **Step 4**: Stress test the pipeline with `scripts/test_speculative_embedding.py` enhancements.
