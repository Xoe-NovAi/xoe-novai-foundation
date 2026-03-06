# Benchmark Test Suite Design: XNAi Foundation

> **Date**: 2026-02-23
> **Context**: JOB-W2-006 - Performance Benchmarking Research
> **Status**: INITIAL DRAFT

---

## 1. Test Scenarios

### 1.1 Scenario: Raw Extraction & Classification
- **Goal**: Measure performance of `extract_content_node` and `classify_content_node`.
- **Input**: 10KB raw markdown (typical manual or scrape).
- **Metrics**: 
  - Time to complete extraction.
  - Accuracy of classification (against Ground Truth).
  - CPU/Memory spike during regex execution.

### 1.2 Scenario: Vector Search (Qdrant)
- **Goal**: Measure retrieval latency and recall.
- **Input**: 100 random queries from the `test-battery.md`.
- **Metrics**:
  - TTFT (Time To First Token) for search results.
  - Search Latency (ms).
  - Recall@5 (Percentage of relevant documents retrieved).

### 1.3 Scenario: End-to-End Distillation
- **Goal**: Measure the full LangGraph pipeline performance.
- **Input**: 50KB complex technical manual.
- **Metrics**:
  - Total processing time.
  - Quality score (using G-Eval).
  - Storage overhead (Metadata size).

---

## 2. Test Environment

- **Profile**: Ryzen 5700U (Sovereign Hardening Expert).
- **Concurrency**: 1, 5, 10, 20 concurrent tasks.
- **Persistence**: Redis enabled, Qdrant in-memory (for speed) and disk-backed (for consistency).

---

## 3. Benchmarking Checklist

1. **Baseline**: Run each test 5 times and record the median/P95 values.
2. **Cold vs. Warm**: Compare the first run (cold) with subsequent runs (warm).
3. **Payload Variance**: Test with 1KB, 10KB, 100KB, and 1MB payloads.
4. **Error Handling**: Measure performance impact when content is rejected by the quality gate.

---

## 4. Automation Plan

- **Step 1**: Use `scripts/phase-5a-stress-test.py` as a base for throughput testing.
- **Step 2**: Create `scripts/benchmark_runner.py` to automate metrics collection.
- **Step 3**: Export results to `benchmarks/reports/SESSION-[DATE].json`.
