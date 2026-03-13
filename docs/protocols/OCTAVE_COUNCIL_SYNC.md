# 🏙️ OCTAVE COUNCIL SYNC: SUB-AGENT BOOT SEQUENCE

## 🎯 OVERVIEW
The **Octave Council (Facets 1-8)** is the ground-level execution layer of the Metropolis. To ensure that every agent acts with the same "Gnostic Context," a standardized **Mesh Sync** is required at the beginning of every session.

## 🏙️ THE 4-STEP MESH SYNC
Every agent MUST verify their connection to the Metropolis Mesh (Ports 8000-8006) before executing any technical task:
1. `curl http://localhost:8000/health` (RAG API): Verify grounded truth connection.
2. `curl http://localhost:8002/health` (CLI Ingress): Verify command access.
3. `curl http://localhost:8005/health` (MCP Context): Verify shared memory bank access.
4. `curl http://localhost:8006/health` (Oikos Mastermind): Verify collective council alignment.

## 🚀 THE SUB-AGENT BOOT SEQUENCE (OCTAVE-SYNC)
1. **Research**: Perform a targeted `grep` and 10-line `read_file` on the `SESSIONS_MAP.md` to identify the current objective.
2. **Strategy**: Propose a plan that adheres to the **STUP Master Protocol** and the **Oikonomia Economics Protocol**.
3. **Execution**: Execute the plan using **Parallel Tool Chains** to maximize efficiency.
4. **Distillation**: Produce a high-density "Mind Dump" (Ambrosia) at the end of the session.

## 🛠️ TOOLS
- `make metropolis-sync`: Sync master settings/MCP/Instructions to all 8 experts.
- `make metropolis-test`: Run the Metropolis Hardening Test Suite (Validate isolation/sync/metrics).
- `make doctor`: Comprehensive system diagnosis to ensure the Octave is healthy.
