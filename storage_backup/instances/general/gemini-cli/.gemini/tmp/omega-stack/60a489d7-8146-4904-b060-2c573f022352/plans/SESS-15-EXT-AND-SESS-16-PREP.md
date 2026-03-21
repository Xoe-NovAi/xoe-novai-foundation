# 🔱 Implementation Plan: Extended Validation, Omega-Align Infra Remediation & SESS-16 Strategy

**Objective**: Validate SESS-15 hardening, remediate zRAM/Swap infrastructure in alignment with the OPUS Strategic Audit (2026-03-08), establish Gemini/Model observability, and research the SESS-16 Image Bloat Audit.

---

## 📍 1. Testing & Validation (SESS-15 Hardening)
**Goal**: Ensure the Librarian and Hydration Protocol are production-ready.

### 🧪 Test Suite (`tests/hardened/`)
- **`test_librarian_resilience.py`**:
    - Mock Redis Stream and inject `session_bloat` events.
    - Verify `zstd` archive creation in `/storage/recall/archives`.
    - Verify `anyio` exponential backoff by simulating Redis connection drops.
- **`test_hydration_atomicity.py`**:
    - Trigger a hydration beat and verify that `INDEX.md`, `activeContext.md`, and `progress.md` are updated with matching coordination keys.

---

## 📍 2. Infrastructure: zRAM & Swap Visibility (OPUS Alignment)
**Goal**: Restore the 16GB zRAM configuration and implement granular visibility to prevent OOM.

### 🛠️ Remediation Steps
- **zRAM Restoration (4GB Fix)**:
    - The user reports a "missing 4GB zRAM swap." Audit indicates a 16GB target. I will aim for the **16GB ZRAM** (as per Audit Task C2) but ensure it's partitioned correctly to provide the "missing 4GB" the user expects.
    - **Configuration**: Use `zramctl` to ensure `/dev/zram0` is initialized with `zstd` compression and the correct `max-device-size`.
- **Visibility & Swap Stats**:
    - Create `scripts/monitor_swap.py`: This script will parse `/proc/swaps` and `/sys/block/zram0/` (total_bytes, comp_data_size, mem_used_total) to provide a real-time "Compression Ratio" metric.
    - Push metrics to VictoriaMetrics: `xnai_zram_compression_ratio`, `xnai_zram_used_bytes`, `xnai_swap_total_bytes`.
- **Memory Over-Commit Guard (Task C2 Fix)**:
    - Update `infra/docker/docker-compose.yml`:
        - Lower RAG API limit: 4GB → 2GB.
        - Lower LLM Server limit: 4GB → 2GB.
        - Implement `mem_reservation` to ensure core services have guaranteed RAM.

---

## 📍 3. Observability Baseline (Gemini & Models)
**Goal**: Quantify Gemini model usage and local model performance.

### 📊 Metrics Audit
- **Gemini Usage Tracking**: 
    - Implement a lightweight `TokenTracker` in `app/XNAi_rag_app/core/metrics.py` to intercept Gemini API calls and record `gemini_input_tokens_total` and `gemini_output_tokens_total`.
    - Track "Actual Model Work Time" (latency of the upstream API call).
- **Cache Efficiency**:
    - Log Redis/Qdrant hits/misses to calculate `xnai_cache_hit_rate`.

---

## 📍 4. SESS-16 Research (Image Bloat Audit)
**Goal**: Identify 1.6GB reduction opportunities through multi-stage refactoring.

### 🔍 Research & Strategy
- **Base Image Pruning**:
    - Move `build-essential`, `cmake`, and `libopenblas-dev` from `Dockerfile.base` to a new `Dockerfile.build_base`.
    - Create a `Dockerfile.runtime_base` that is strictly `python:slim` + runtime libs (`libopenblas0`, `libgomp1`).
- **Dependency Audit**:
    - Identify if `torch` or other heavy ML libs are being pulled into images where they aren't needed (e.g., MkDocs or Caddy).
- **Multi-Stage Blueprint**:
    - Redesign `infra/docker/Dockerfile` to copy only the `site-packages` and application code, omitting build-time artifacts.

---

## 🛠️ Implementation Phasing

### Phase A: Infrastructure & Diagnostics
- [ ] Initialize/Fix zRAM to 16GB (ensuring the missing 4GB is recovered).
- [ ] Deploy `monitor_swap.py` and verify metrics in Grafana.
- [ ] Apply Docker Compose memory limit reductions (Task C2).

### Phase B: Observability
- [ ] Implement Gemini token tracking in `metrics.py`.
- [ ] Run a baseline test to verify "Model Work Time" metrics.

### Phase C: SESS-15 Validation
- [ ] Execute `tests/hardened/` and document results.

### Phase D: SESS-16 Preparation
- [ ] Create the `SESS-16-STRATEGY.md` with the new Multi-Stage Docker architecture.

---

## 🧪 Verification
- **Swap**: `zramctl` shows 16GB capacity; `free -h` shows correct swap space.
- **Metrics**: Grafana "Omega Dashboard" shows Gemini token consumption.
- **Resilience**: Librarian handles simulated session bloat without OOM.
