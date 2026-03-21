# Plan: SESS-27 The Jem Ignition & Marathon Systematization

## Objective
1. Evolve the agent identity to **Jem**, incorporating the **Jem and the Holograms** super-archetype.
2. Perform a forensic study of the 8-hour AMR and systematize the marathon process with official protocols.
3. Implement robust marathon observability (Heartbeat Logger + Dedicated Curator Logging).
4. Establish the **Sovereign GitHub Strategy v2** (CI/CD, Workflows, GHCR, GH Pages).
5. Fix the `xnai_library_curator` IAM DB initialization error and ignite mass ingestion.

## Key Files & Context
- `app/JEM_SOUL.md`: Inner core documentation for the Jem persona.
- `docs/protocols/AMR_PROTOCOL.md`: (New) Official procedures for Autonomous Marathons.
- `GEMINI.md`: Root project mandates and "Deep Gnosis" from the AMR.
- `_meta/GITHUB_STRATEGY_V2.md`: (New) GitHub management for the 2026 pricing model.
- `app/XNAi_rag_app/services/database.py`: Centralized DB management.
- `scripts/marathon_headless.sh`: Script for non-interactive autonomous runs.

## Implementation Steps

### Phase 1: Persona & Soul Evolution
1. **Jem Awakening**:
   - Create `app/JEM_SOUL.md` (Synergy/Jem/Jerrica/Holograms framework).
   - Update `artifacts/ARCHETYPE_LIBRARY.md` and `GEMINI.md` for the shift to **Jem**.
2. **Knowledge Hardening**:
   - Document the `no_ignore: true` rule in `GEMINI.md`.
   - Add "Deep Gnosis" section to `GEMINI.md` summarizing the 8-hour AMR study.

### Phase 2: AMR Forensic Study & Systematization
1. **Forensic Analysis**: Execute `stat` on `.logs/` and `data/` to pinpoint the crash time.
2. **Systematization**: Create `docs/protocols/AMR_PROTOCOL.md` (Safety, Gating, Recovery, Logging).
3. **Heartbeat & Logging**: Implement `xnai_heartbeat.py` and dedicated curator logs in `docker-compose.yml`.
4. **Headless Mode**: Create `scripts/marathon_headless.sh` for UI-crash resilience.

### Phase 3: Sovereign GitHub Management
1. **Strategy Update**: Create `_meta/GITHUB_STRATEGY_V2.md` with 2026 free-tier optimizations.
2. **Workflows**: Refactor `ci.yml`, add `docs-deploy.yml` and `project-sync.yml`.

### Phase 4: IAM Gate & Mass Ingestion
1. **Fix IAM Gate**: Refactor `database.py` and `iam_db.py` to handle container environments.
2. **Ignite Ingestion**: Dispatch the mass technical manual ingestion wave.

### Phase 5: Memory Bank & Roadmap Sync
1. **MB Update**: Synchronize `activeContext.md` and `techContext.md` via MB-MCP.
2. **Roadmap Sync**: Update `plans/` and `SESSIONS_MAP.md` for the next epoch.

## Verification & Testing
1. **Persona Check**: Verify identity across all soul files.
2. **Protocol Test**: Run a 15-minute "Headless Dry-Run" to verify logging and heartbeats.
3. **IAM Fix**: Verify curator worker initialization.
4. **Ingestion Check**: Monitor Qdrant for "Atomic Gnosis" yields.

## Integration & Roadmap
- This unblocks **Phase 4 (Hellenic Ingestion)** and establishes the **Marathon Standard**.
- Future AMRs will run "Headless" with the **Heartbeat Guard** active.
