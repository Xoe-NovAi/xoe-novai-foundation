# Plan: Omega Chronicle & Sentinel Integration (SESS-17 FINAL)

## 🎯 Objective
Implement a **Cybernetic Self-Awareness** layer for the Omega Stack by correlating Agentic Intent (Mind) with Physical Telemetry (Machine). This system ensures architectural continuity across session compressions and provides a "Black Box" for agent reasoning, while enabling local models with limited context to perform at higher levels via high-density state injection.

## 🏗 Components

### 1. `scripts/omega_chronicle.py` (The Synthesis Engine)
- **Mind**: Reads Gemini session data (tokens, requests) from `artifacts/omega_instance_metrics.json`.
- **Machine**: Reads local system metrics (CPU, RAM, Disk, Load) via the **Stats MCP** or `psutil`.
- **Edge**: Detects and records the footprint of the local `llama_cpp.server`.
- **Output**: Generates a Markdown "Chronicle" entry in `memory_bank/chronicles/`.
- **New**: Integrated as a tool within the **Memory Bank MCP**.

### 2. `memory_bank/chronicles/` (Persistent Storage)
- A new directory to store temporal snapshots of the stack's state.
- Acts as a "Level 2 Cache" for agent memory.
- Stores "High-Density Mind Dumps" for local model context injection.

### 3. `scripts/context_watchdog.sh` (The Automation Trigger)
- A lightweight script to monitor `.logs/sessions/` for changes.
- Triggers `omega_chronicle.py --reason "Automatic Session Update"` whenever a session is modified or `/compress` occurs.

### 4. `Vikunja` Integration (The Executive Bridge)
- Automatically creates "Distillation" tasks in Vikunja when architectural entropy is detected in a Chronicle.

## 📋 Implementation Steps

### Phase 1: Infrastructure & Automation
- Create `memory_bank/chronicles/`.
- Deploy `scripts/omega_chronicle.py` (Refactored for MCP).
- Deploy `scripts/context_watchdog.sh`.

### Phase 2: Knowledge Integration
- Ingest Cline's Documentation Foundation into the reasoning graph.
- Update `SESSIONS_MAP.md` to reflect the completion of the "Great Reconciliation" (SESS-17).
- Define the **Sentinel Skill** via `skill-creator`.

### Phase 3: Final Verification
- Verify the **Sentinel-to-Grafana** annotation pipeline.
- Test the **High-Density Snapshot Injection** for local models.

## 🧪 Verification & Testing
1. **Manual Trigger**: Run `python3 scripts/omega_chronicle.py --reason "Test Snapshot"` and verify the Markdown output.
2. **Resource Check**: Confirm that the script correctly distinguishes between Gemini CLI (Cloud) and Local Llama (PID-based) memory usage.
3. **Disk Guard**: Verify that the Chronicle includes a warning if the 93% root disk threshold is exceeded.

## 🚀 Migration & Rollback
- **Migration**: None required; this is a non-breaking additive feature.
- **Rollback**: Delete `scripts/omega_chronicle.py` and remove the `memory_bank/chronicles/` directory.
