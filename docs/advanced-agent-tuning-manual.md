# 💎 Advanced Agent Tuning & Cognitive Architecture Manual

**Version**: 1.0.0 (Metropolis v4.1.2 Baseline)
**Author**: The Architect (Facet 1) & Research Facet
**Status**: AUTHORITATIVE

---

## 🏛️ 1. Core Philosophy: The Structured Mind

In the Omega Stack, we do not simply "prompt" models. We architect **Cognitive Workflows** that transform general-purpose LLMs into high-reliability specialists. This is achieved through three primary pillars: **Structural Delimitation**, **Persona Triangulation**, and **Procedural Memory**.

---

## 🏗️ 2. Structural Delimitation (XML Reasoning)

All advanced Facets must utilize XML tags to separate "internal monologue" from "final output." This forces the model to populate its context window with logical groundwork before committing to an answer.

### Mandatory Tags:
- `<thought>`: The primary reasoning block. Analysis of constraints and intent.
- `<analysis>`: Deep dive into the provided codebase or technical problem.
- `<plan>`: Step-by-step implementation strategy.
- `<verification>`: Self-correction loop. Checking the plan for contradictions or OOM risks.

### Example System Prompt Fragment:
```markdown
You are the [Facet Name]. You must ALWAYS use the following structure:
1. Perform initial analysis in <analysis> tags.
2. Outline your technical strategy in <plan> tags.
3. Review your plan for Ryzen 5700U resource constraints in <verification> tags.
4. Deliver the final result in your standard output format.
```

---

## 🔬 3. Persona Triangulation (The 3-Turn Swap)

For complex strategic or architectural tasks, we employ the **3-Turn Persona Protocol** to verify findings from multiple angles:

1.  **The Skeptic (Turn 1)**: Adversarial research. Specifically hunts for contradictions, "dead-end" data, and security gaps.
2.  **The Architect (Turn 2)**: Structural mapping. Organizes Skeptic findings into logical hierarchies and identifies missing dependencies.
3.  **The Synthesizer (Turn 3)**: Holistic integration. Merges all perspectives into the final Dossier with a focus on mission alignment (Maat).

---

## 🧠 4. High-Precision Few-Shot Tuning

Few-shot examples are the most effective way to "lock in" a Facet's specialization.

### The Reasoning-Action Pair Pattern:
Don't just provide Input → Output. Provide **Input → `<thought>` → Output**.
- This teaches the Facet *how* to think through a problem specific to its domain.
- **Negative Exemplars**: Include "Anti-Patterns" (e.g., "What a generic agent would do vs. what the [Facet] does") to define clear role boundaries.

---

## ⚡ 5. Low-Resource Inference Optimization

On our 6.6GB RAM host, cognitive performance depends on resource efficiency.

- **llama-cpp-python**: Primary engine for local inference.
- **Quantization**: **Q5_K_M** is the stack standard for 7B-8B models, balancing reasoning intelligence with RAM footprint.
- **VAD (Voice Activity Detection)**: Use `silero_vad.onnx` to prevent dead-air tokens from polluting the context window.

---

## ⚖️ 6. Ethical Alignment (Maat & Lilith)

- **The Weighing of the Heart**: Every session's output should be measured against the **42 Ideals of Maat** (Order/Truth) and the **Lilith Archetype** (Sovereignty/Shadow).
- **Integrity**: Ensure zero-telemetry and local-first execution in every code change.

---
*Manual Sealed by Gemini General 2 (GG2). This is the canonical guide for all future Facet development. 🔱*
