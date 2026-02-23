# Research: LLM Performance Benchmarking Methodologies

> **Date**: 2026-02-23
> **Author**: GEMINI-MC
> **Status**: INITIAL DRAFT
> **Context**: JOB-W2-006 - Performance Benchmarking Research

---

## 1. Core Performance Metrics

Evaluating LLM performance requires consistent, reproducible metrics. These provide insights into both user experience (responsiveness) and system efficiency (cost/throughput).

### 1.1 Latency Metrics (Responsiveness)
| Metric | Full Name | Description | Target (XNAi) |
|--------|-----------|-------------|---------------|
| **TTFT** | Time To First Token | Time from prompt submission to first visible character. | < 300ms |
| **TPOT** | Time Per Output Token | Average time between consecutive tokens. | < 50ms |
| **E2E** | End-to-End Latency | Total duration for the entire response. | < 5s |

### 1.2 Throughput Metrics (Efficiency)
| Metric | Full Name | Description |
|--------|-----------|-------------|
| **TPS** | Tokens Per Second | Total tokens generated divided by time (E2E). |
| **RPS** | Requests Per Second | Concurrent request handling capacity. |

### 1.3 Quality-Correctness Tradeoff
- **ROUGE/BLEU**: Traditional text similarity metrics (less relevant for reasoning).
- **G-Eval**: Using a high-reasoning LLM to score another's output.
- **Human Eval**: Manual expert review (Gold Standard).

---

## 2. Vector DB (Qdrant) Performance Patterns (W2-006-3)

Vector databases like Qdrant exhibit specific performance characteristics based on the index type and hardware.

### 2.1 Indexing & Search
- **HNSW (Hierarchical Navigable Small World)**:
  - *Fast Search*: O(log N) search time.
  - *Slow Indexing*: Significant memory/CPU cost during insertions.
  - *Memory-Intensive*: Stores large graph structures in RAM.
- **Quantization (Scalar/Product)**:
  - *Pros*: Reduces memory footprint by 4x-8x.
  - *Cons*: Slight loss in search accuracy (recall).

### 2.2 Bottlenecks
- **Embedding Generation**: Latency is often dominated by the embedding model (e.g., `sentence-transformers`) rather than the search itself.
- **I/O Bound**: Disk-based Qdrant instances will be much slower than in-memory ones.

---

## 3. Benchmarking Best Practices (W2-006-4)

1. **Warmup**: Always run several "warmup" requests to initialize models/caches before measuring.
2. **Concurrency**: Test with varying numbers of concurrent users (1, 10, 50, 100) to find the "knee" in the latency curve.
3. **Reproducibility**: Use fixed seeds for generation and consistent hardware environments (Ryzen 5700U profile).
4. **Tooling**: Use tools like `locust` for load testing and `prometheus` for resource monitoring.

---

## 4. Next Steps
- Design the benchmark test suite in `benchmarks/BENCHMARK-DESIGN.md`.
- Implement a simple TTFT/TPS tracker in `app/XNAi_rag_app/core/metrics.py`.
