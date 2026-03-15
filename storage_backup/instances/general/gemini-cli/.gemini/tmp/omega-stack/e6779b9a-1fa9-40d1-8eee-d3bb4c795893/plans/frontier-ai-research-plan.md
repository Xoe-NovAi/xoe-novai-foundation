# 🚀 Research Plan: Frontier AI "Mind-Machine" Synthesis (2026)

## 🎯 Objective
Develop the expertise and technical frameworks to implement **Cybernetic Self-Awareness** in the Omega Stack. This involves bridging the gap between high-level agentic intent (Mind) and low-level system performance (Machine) through automated telemetry correlation and state persistence.

---

## 🔍 Core Knowledge Gaps

1.  **KV-Cache Persistence & "Hot-Swapping"**:
    *   *Problem*: When an agent session compresses or a local model restarts, the "mental momentum" (KV-cache) is lost.
    *   *Research Goal*: Investigate if `llama-cpp-python` or the RAG API can serialize and restore KV-caches to the Sovereign Library partition.

2.  **Semantic-Metric Correlation**:
    *   *Problem*: We have logs (semantic) and Prometheus data (metric), but no unified "Self-Correction" logic that says, "Task X caused Latency Y, therefore use Model Z."
    *   *Research Goal*: Develop a data schema for "Chronicles" that enables machine-learning-ready correlation between task types and hardware footprints.

3.  **Autonomous Context Pruning**:
    *   *Problem*: `/compress` is manual and binary.
    *   *Research Goal*: Research "Ranked-Attention Pruning"—automatically dropping low-signal entities from the active context based on their "Success Rate" in the PES (Persistent Entity System).

---

## 🛠 Tiered Research Workflow

### Tier 1: Infrastructure Telemetry (The Machine)
- **Investigation**: Deep dive into VictoriaMetrics `node_exporter` and Grafana's Annotation API.
- **Goal**: Create a "Telemetry Hook" that can be triggered by a shell command to mark "Mental Events" on the system graphs.
- **Reference**: `scripts/enhanced-monitoring.py`.

### Tier 2: Local Context Management (The Edge Mind)
- **Investigation**: Research `llama-cpp`'s `--cache-type-k` and `--cache-type-v` (FP16 vs Q8) for Zen 2 (Ryzen 5700U) optimization.
- **Goal**: Determine the "Memory-to-Reasoning" ratio for local models (e.g., Qwen 2.5 7B) on our specific hardware.
- **Reference**: `app/config.toml` [models] section.

### Tier 3: The "Sentinel" Logic (The Synthesis)
- **Investigation**: Prototype the `omega_chronicle.py` logic.
- **Goal**: Synthesize the "Active Context Dump" with real-time `psutil` data.
- **Reference**: `memory_bank/activeContext.md`.

---

## 📋 Phase 1 Action Items (SESS-17 to SESS-18)

1.  **[RESEARCH]**: Read `llama-cpp-python` documentation regarding context serialization (`save_state`/`load_state`).
2.  **[PROTOTYPE]**: Create `scripts/omega_observer.py` to pull local metrics and push to a Markdown "Chronicle."
3.  **[EXPERIMENT]**: Trigger a large PES batch update and correlate the RAM spike in Grafana with the "Mind Dump" timestamp.
4.  **[REFINE]**: Update the `Model Router` to include "Hardware Constraints" (e.g., "Don't use Local Llama if RAM > 90%").

---

## 📚 Resources & Reading List
- **Documentation**: `docs/microservices/docgen/models.py` (Current state).
- **External**: Llama.cpp Context Caching (GitHub Discussions).
- **Internal**: `INDEX.md` (Spatial Partitioning).

## 🏁 Success Criteria
- [ ] An automated "Chronicle" is generated every time `/compress` occurs.
- [ ] The agent can describe its own "Hardware Footprint" in terms of RAM and Token Latency.
- [ ] We have a working prototype of a "Self-Halting" agent that stops before hitting the 95% disk threshold.
