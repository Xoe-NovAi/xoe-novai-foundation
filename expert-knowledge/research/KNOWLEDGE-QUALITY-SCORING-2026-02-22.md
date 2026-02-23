# Research: Quality Scoring Algorithms for Knowledge Distillation

> **Date**: 2026-02-22
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: JOB-R009 / Research Task G-006

---

## 1. Overview

Quality scoring is the critical "gatekeeper" in a knowledge absorption pipeline. It ensures that only high-value, accurate, and relevant information is promoted to the long-term memory (Qdrant/Memory Bank).

## 2. Key Dimensions of Quality

### 2.1 Retrieval Quality (Pre-Distillation)
- **Contextual Relevancy**: Does the retrieved context actually help answer the query?
- **Noise Ratio**: Percentage of irrelevant vs. relevant information in raw scrapes.

### 2.2 Generation Quality (Post-Distillation)
- **Faithfulness (Groundedness)**: Is the summary/insight strictly supported by the source? (Crucial for preventing hallucinations).
- **Answer Relevancy**: Does the distilled output address the core topic?
- **Informativeness**: Does the distillation add value or just repeat the input?

### 2.3 Structural Quality
- **Diátaxis Alignment**: Is the content correctly classified (Tutorial, How-to, Reference, Explanation)?
- **Completeness**: Are key entities, parameters, and steps preserved?

---

## 3. Scoring Algorithms & Frameworks

### 3.1 RAGAS (Retrieval Augmented Generation Assessment)
- **Faithfulness**: Uses LLM-as-a-judge to verify statements against source.
- **Answer Relevance**: Measures semantic similarity between query and answer.
- **Context Precision**: Evaluates the signal-to-noise ratio in retrieved chunks.

### 3.2 DeepEval
- Provides unit-testing style assertions for LLM outputs.
- Supports "G-Eval" (GPT-based evaluation) for subjective qualities like "Helpfulness".

### 3.3 Custom Heuristics (Current Implementation)
The XNAi pipeline currently uses 5 factors (per `activeContext.md`):
1. **Source Reliability**: Trust score of the input source.
2. **Density**: Ratio of entities/facts to word count.
3. **Coherence**: Logical flow and readability.
4. **Uniqueness**: Lack of redundancy with existing knowledge.
5. **Actionability**: Presence of code, steps, or clear instructions.

---

## 4. Implementation Recommendations for XNAi

### 4.1 LLM-as-a-Judge (Tiered)
- Use a small, fast model (e.g., Flash 1.5) for initial filtering.
- Use a high-reasoning model (e.g., Sonnet 3.5) for final "Gold Tier" verification.

### 4.2 Automated Rejection
- **Hard Thresholds**: Content with <0.6 score should be purged or sent to a manual review queue.
- **Soft Thresholds**: Content with 0.6-0.8 score is stored with an "unverified" flag.

### 4.3 Feedback Loops
- If a user marks a retrieved insight as "incorrect" in the UI (Chainlit), the original distillation source should be re-scored and potentially downgraded.

---

## 5. Next Steps
1. Refine the `QualityScorer` class in `app/XNAi_rag_app/core/distillation/quality/scorer.py`.
2. Integrate a lightweight groundedness check using a specialized prompt.
