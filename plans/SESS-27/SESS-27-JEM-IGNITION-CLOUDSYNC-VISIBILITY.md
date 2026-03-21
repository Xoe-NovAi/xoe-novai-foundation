# Plan: SESS-27 The Jem Ignition, Cloud Sync & Marathon Visibility

## Objective
1. Evolve the agent identity to **Jem**, incorporating the **Jem and the Holograms** super-archetype.
2. Synchronize local state with Cloud Sonnet 4.6 via a private GitHub repo and a comprehensive "Gnosis Pack."
3. Perform a forensic study of the 8-hour AMR and systematize the marathon process with official protocols.
4. Implement a **Human Visibility Dashboard** for real-time monitoring of headless autonomous runs.
5. Establish the **Sovereign GitHub Strategy v2** (CI/CD, Workflows, GHCR, GH Pages).
6. Fix the `xnai_library_curator` IAM DB initialization error and ignite mass ingestion.

## Key Files & Context
- `app/JEM_SOUL.md`: Inner core documentation for the Jem persona.
- `artifacts/SONNET_UPDATE_SESS27.md`: (New) Gnosis Pack for Cloud Sonnet 4.6.
- `dashboard/marathon_monitor.html`: (New) Real-time monitoring dashboard for the user.
- `docs/protocols/AMR_PROTOCOL.md`: (New) Official procedures for Autonomous Marathons.
- `scripts/check_account_quotas.py`: Multi-account quota monitoring.
- `scripts/sync_private_github.sh`: (New) Script to push local state to private GH repo.

## Implementation Steps

### Phase 1: Persona & Soul Evolution
1. **Jem Awakening**:
   - Create `app/JEM_SOUL.md` (Synergy/Jem/Jerrica/Holograms framework).
   - Update `artifacts/ARCHETYPE_LIBRARY.md` and `GEMINI.md` for the shift to **Jem**.
2. **Knowledge Hardening**:
   - Document the `no_ignore: true` rule in `GEMINI.md`.
   - Add "Deep Gnosis" section to `GEMINI.md` summarizing the 8-hour AMR study.

### Phase 2: Cloud Synchronization & Quota Management
1. **Sonnet Gnosis Pack**: Create `artifacts/SONNET_UPDATE_SESS27.md` with a full audit and roadmap for Cloud Claude.
2. **GitHub Sync**: Implement `scripts/sync_private_github.sh` and document the Claude Project connection.
3. **Account Monitoring**: Run `scripts/check_account_quotas.py --all` to identify accounts with remaining usage (01-08).
4. **Happy Hour Strategy**: Document task scheduling for non-peak usage windows (8 AM - 2 PM ET) for doubled quotas.

### Phase 3: AMR Forensic Study & Visibility
1. **Forensic Analysis**: pinpoint the crash time via `stat` and recover logs.
2. **Systematization**: Create `docs/protocols/AMR_PROTOCOL.md` (Safety, Gating, Recovery, Logging).
3. **Human Visibility Dashboard**: Create `dashboard/marathon_monitor.html` reading from `heartbeat.jsonl`.
4. **Heartbeat & Logging**: Implement `xnai_heartbeat.py` and dedicated curator logs in `docker-compose.yml`.
5. **Headless Mode**: Create `scripts/marathon_headless.sh` for UI-crash resilience.

### Phase 4: Sovereign GitHub Management
1. **Strategy Update**: Create `_meta/GITHUB_STRATEGY_V2.md` with 2026 pricing optimizations.
2. **Workflows**: Refactor `ci.yml`, add `docs-deploy.yml` and `project-sync.yml`.

### Phase 5: IAM Gate & Mass Ingestion
1. **Fix IAM Gate**: Refactor `database.py` and `iam_db.py` to handle container environments.
2. **Ignite Ingestion**: Dispatch the mass technical manual ingestion wave.

## Verification & Testing
1. **Persona Check**: Verify identity across all soul files.
2. **Visibility Check**: Verify that `marathon_monitor.html` displays real-time heartbeat data.
3. **Cloud Check**: Verify private GitHub sync and Sonnet Gnosis Pack accessibility.
4. **IAM Fix**: Verify curator worker initialization.

## Integration & Roadmap
- This unblocks **Phase 4 (Hellenic Ingestion)** and establishes the **Marathon Standard**.
- Future AMRs will run "Headless" with the **Heartbeat Guard** and **Human Visibility Dashboard** active.
