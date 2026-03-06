# Advanced RAG Roadmap (Xoe-NovAi Pioneer Layer)

## 🎯 Vision
Melding the "Metropolis" persistent expert system with state-of-the-art retrieval patterns to achieve sub-second draft latency and 99% factual grounding.

## 🧬 Phase 1: Speculative RAG (Shipped)
- **Concept**: Generate a "Draft Answer" immediately using Level 1 (150M) and 128d speculative embeddings.
- **Validation**: High-fidelity models (8B+) validate the draft in the background as the user begins reading.
- **Implementation**: `EscalationResearcher._run_speculative_draft()`.

## 🧠 Phase 2: Hierarchical Multi-Stage Retrieval
- **Mechanism**: **Small-to-Big**. 
    - Store 128-byte "Summary Chunks" for high-speed speculative hits.
    - Link to 4kb "Context Blocks" for the final Authority round.
- **Goal**: 3x reduction in vector database IO latency.

## 🎭 Phase 3: Persona-Driven HyDE
- **Concept**: **Hypothetical Document Embeddings (Persona-Led)**.
- **Workflow**: 
    1. Kurt Cobain generates a "phantom response" to a query.
    2. We search for RAG docs similar to Kurt's phantom response.
    3. Result: Dramatic increase in thematic relevance.

## 🏗️ Phase 4: LongRAG & RAPTOR
- **LongRAG**: Process entire documents as single context blocks once 128k context models are standard.
- **RAPTOR**: Recursive abstractive processing for tree-based retrieval (Summaries of Summaries).

---
**Custodian**: Gemini CLI
**Date**: 2026-03-01
