# RESEARCH WORKFLOW PROTOCOL v1.0
**Status**: 🟢 ACTIVE | **Domain**: Scholarly Research & Synthesis

---

## 🎯 OBJECTIVE
Provide high-quality, scholarly synthesis of classical and technical works by utilizing local inference for retrieval and powerful synthesis for final reporting.

---

## 🔄 THREE-STAGE REFINEMENT WORKFLOW

### Stage 1: Local Retrieval & Extraction (Retrieval)
- **Model**: Local domain-specific BERT (Ancient Greek, Philosophy) or `Gemma-3-4b`.
- **Action**: Fetch sources from Qdrant/FAISS.
- **Goal**: Identify key quotes, data points, and context.
- **Output**: Raw citation blocks and brief summaries.

### Stage 2: Structural Structuring (Medium Reasoning)
- **Model**: Local `Phi-2-OmniMatrix` or `RocRacoon-3b`.
- **Action**: Organize the raw citations into a logical structure (Arguments, Counter-arguments, Historical context).
- **Goal**: Create a coherent "Research brief".
- **Output**: Structured Markdown outline.

### Stage 3: High-Reasoning Synthesis (Synthesis)
- **Model**: Cloud `Gemini 1.5 Pro`, `Claude 3.5 Sonnet`, or `Haiku`.
- **Action**: Final scholarly synthesis, cross-referencing, and stylistic polish.
- **Goal**: Produce the final research report.
- **Output**: Scholarly Research Paper / Report.

---

## ⚖️ QUALITY GATING & METRICS

For scholarly ingestion and research, we track the following metrics:

| Metric | Threshold | Method |
| :--- | :--- | :--- |
| **Retrieval Hit Rate** | > 85% | Automated testing against ground truth |
| **Citation Accuracy** | 100% | Cross-reference checks against local MD library |
| **Scholarly Tone** | High | LLM-as-a-Judge (ChainForge) |
| **Semantic Precision** | 0.90+ | FAISS/Qdrant similarity scores |

---

## 🛠 TOOL UTILIZATION

- **Qdrant**: Primary vector store for persistent scholarly metadata.
- **Redis**: Agent Bus communication and task queuing.
- **Vikunja**: Task tracking for long-running research jobs.
- **Chainlit**: UI for interactive natural language research requests.
- **FAISS**: Fast local retrieval for large classical corpora.
- **Crawl4AI**: Deep-crawled documentation and library sources.
