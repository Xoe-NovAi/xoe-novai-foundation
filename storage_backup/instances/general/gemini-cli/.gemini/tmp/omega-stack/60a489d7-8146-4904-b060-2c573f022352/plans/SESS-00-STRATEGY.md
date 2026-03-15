# 🏙️ Metropolis Session Orchestration: SESS-00 Hardening & Multi-Facet Strategy

**Goal**: Prepare the Gemini CLI for high-throughput, multi-facet agentic workflows within the 6.6GB RAM budget.

---

## 🔱 SESS-00: Gemini CLI Hardening (Priority)
**Focus**: Optimize internal features and settings for the Metropolis Mesh.

### 🛠️ Key Optimization Tasks
1.  **Skills Implementation**: Audit and activate built-in skills (e.g., `skill-creator`).
2.  **Extensions Research**: Define "Extensions" in the context of Gemini 2026 (likely MCP-bridge or Tool-extensions).
3.  **Compression Calibration**: Fine-tune `compressionThreshold` for 6.6GB RAM.
    *   *Current*: 0.6
    *   *Target*: 0.7-0.8 (aggressive compression to maximize context lifespan).
4.  **OOM Protection**: Research `max_old_space_size` for Node.js to stabilize the CLI during deep investigative turns.

---

## 🏗️ Multi-Facet Parallelism (Metropolis Protocol)

### 🏎️ Execution Command (Pattern)
To run parallel instances without race contention:
```bash
# Session A (Researcher)
gemini-cli --agent facet-3 --session sess-16-research --otlp-port 4317

# Session B (Implementer)
gemini-cli --agent facet-8 --session sess-16-build --otlp-port 4318
```

### 🛡️ Safety Guards
*   **Unique OTLP Ports**: Prevents Jaeger telemetry overlap.
*   **Session Isolation**: Separate `.history` files to prevent context bleeding.
*   **MB-MCP Consistency**: Centralized state via Port 8005 (SSE/FastAPI).

---

## 📅 Refined SESS-16: Image Audit & Build Optimization
**Recommended Summons**:
*   **Facet 6 (Infra)**: Layer Analysis & Build Cache Optimization.
*   **Facet 8 (DevOps)**: Dockerfile refactoring & base image reduction.
*   **Facet 1 (Scribe)**: Documentation & Master Index Sync.

---

## 🔑 SESS-23: High-Throughput Bridge (Auth Rotation)
**Goal**: Implement non-interactive OAuth/API rotation to tap 10,000 RPD.
*   **Strategy**: Use `scripts/quick_gemini_setup.sh` to refresh tokens.
*   **Automation**: Create a `rotation-manager` service that switches `.env` keys on 429.

---
*Strategy sealed by Gemini General. Proceed to SESS-16 with multi-facet readiness.* 🔱
