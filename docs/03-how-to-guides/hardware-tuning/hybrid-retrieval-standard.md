# Hybrid Retrieval: The RRF Gold Standard
**Status**: Elite Hardened
**Logic**: Reciprocal Rank Fusion & Lexical Tie-Breaking
**Goal**: 91%+ Retrieval Accuracy

## 1. The Dual-Engine Strategy
Xoe-NovAi achieves enterprise-grade retrieval precision by combining the strengths of semantic and lexical search.

- **Engine A: FAISS (Dense)**: Captures conceptual meaning and fuzzy relationships.
- **Engine B: Neural BM25 (Lexical)**: Captures exact technical terms, version numbers, and unique identifiers.

---

## 2. Reciprocal Rank Fusion (RRF)
We use **RRF ($k=60$)** to aggregate results from both engines. RRF is superior to raw score averaging because it is scale-agnostic and prioritizes documents that appear high in both lists.

### 2.1 The RRF Formula
The score for a document $d$ is calculated as:
$$score(d) = \sum_{r \in R} \frac{1}{k + rank(d, r)}$$
*Where $R$ is the set of retrievers and $k$ is the smoothing constant (default 60).*

### 2.2 Alpha-Weighting
Users can tune the priority of the engines via the `alpha` parameter (0.0 to 1.0):
- **Alpha 0.7+**: Prioritizes **BM25** (Best for technical documentation and "How-to" lookups).
- **Alpha 0.3-**: Prioritizes **FAISS** (Best for conceptual "What-is" questions and creative brainstorming).

---

## 3. Advanced Tie-Breaking
In the event of an RRF score collision (where two documents have identical aggregated ranks), the system uses the **Raw BM25 Score** as the tie-breaker. This ensures that exact keyword matches are always elevated above fuzzy semantic matches when the ranking is otherwise equal.

---

## 4. Metadata Filtering (ABAC-Ready)
The retrieval engine supports deep metadata filtering before the RRF fusion occurs.

- **Version Control**: Filter results by specific project versions.
- **Category Isolation**: Restrict search to specific Diátaxis quadrants (e.g., only "Tutorials").
- **Author/Tag Filters**: Scoped retrieval based on organizational metadata.

---

## 5. Concurrency & Integrity
### 5.1 File Locking (flock)
To prevent **Segment Violations** during concurrent operations (e.g., searching while the Crawler is mid-ingestion), the system implements mandatory **Advisory File Locking**.
- **Implementation**: Every index read/write is wrapped in a `fcntl.flock` context manager.

### 5.2 Atomic Persistence
FAISS indexes are persisted using the **Pattern 4 (fsync)** standard, ensuring that crashes during ingestion do not leave the index in a corrupted state.

---

## 6. Tuning SOP
1.  **Monitor Accuracy**: Use the `rag_relevance_score` metric in Grafana.
2.  **Adjust Alpha**: If users report "fuzzy" answers to technical questions, increase Alpha to 0.7.
3.  **Optimize NProbe**: For large datasets (>10k vectors), use `retriever.optimize_index()` to auto-tune search parameters based on your current hardware latency.
