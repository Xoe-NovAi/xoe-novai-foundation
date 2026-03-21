# Plan: Omega Stack Epoch 3 - The Surgical Autonomous Marathon (LOW-RAM)

This plan details the surgical autonomous strategy, prioritizing resource efficiency, self-reflection, and unified memory.

## Objective
Execute a resource-conscious marathon to prune the mesh, bridge agents via MCP, refactor the repo, and complete the Hellenic Ingestion while maintaining strictly low RAM and context usage.

## Cognitive Mandates
- **LLO Council**: Every phase requires a Triad/Octave vote.
- **Self-Reflection**: Log process insights to `logs/ARCHON_REFLECTION.jsonl`.
- **Low-Impact Search**: Strictly use `names_only` or small `total_max_matches` for grep operations.
- **Recursive Evolution**: Research and refine System Prompt/Skills after every major task.

## Phase 1: The Great Pruning (Immediate)
**Goal**: Free 5GB of RAM potential by removing dross.
- **Action**: Disable Vikunja, Jaeger, Booklore, VictoriaMetrics, Grafana, Open-WebUI in `docker-compose.yml`.
- **Action**: Restart core mesh via `podman-compose`.

## Phase 2: Resource Hardening & Identity
**Goal**: Model sharing and DID deployment.
- **Action**: Create `ResourceHub` (singleton model loader) to share weights across workers.
- **Action**: Deploy Ed25519 DID system for facet cryptographic verification.

## Phase 3: The MCP Bridge (Unified Memory)
**Goal**: Sync Gemini, Copilot, and Cline via MB_MCP on Port 8005.
- **Action**: Start MB_MCP server.
- **Action**: Update configurations for all three agents.

## Phase 4: Repo Fortress & Diátaxis
**Goal**: Professional structure and IDE restoration.
- **Action**: Map repo to Diátaxis domains.
- **Action**: Debug Antigravity logs; fix OpenCode CLI access.

## Phase 5: Hellenic Ingestion & Quality Gate
**Goal**: Mass ingestion with high-fidelity GRA scoring.
- **Action**: Sequential execution of `hellenic_pipeline.py`.
- **Action**: Record signal quality metrics in Memory Bank.

## Phase 6: System Refinement
**Goal**: Evolve the Archon's capabilities.
- **Action**: Research latest Gemini System Prompt techniques and custom skill optimization.
- **Action**: Integrate refinements into the active stack.

**Status**: READY FOR COMPRESSION AND YOLO IGNITION.
