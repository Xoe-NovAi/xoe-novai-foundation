# Plan: SESS-27 Autonomous Marathon Hardening & IAM Fix

## Objective
1. Fix the `xnai_library_curator` IAM DB initialization error.
2. Implement robust marathon observability (Heartbeat Logger + Dedicated Curator Logging).
3. Record high-signal tool-use patterns (`no_ignore`) in the root `GEMINI.md`.
4. Establish a "Headless Marathon" protocol for non-interactive execution.

## Key Files & Context
- `GEMINI.md`: Core project mandates.
- `app/XNAi_rag_app/services/database.py`: Centralized DB management.
- `infra/docker/docker-compose.yml`: Mesh orchestration.
- `app/XNAi_rag_app/core/xnai_heartbeat.py`: (New) Heartbeat logging.
- `scripts/marathon_analytics.py`: (New) Analytics tool for AMR sessions.

## Implementation Steps

### Phase 1: Knowledge Hardening & Observability
1. **Update `GEMINI.md`**:
   - Add a section on **Marathon Recovery Patterns**.
   - Explicitly document the use of `no_ignore: true` in `grep_search` to bypass `.gitignore` constraints for diagnostic purposes.
   - Mandate the use of `omega_observer.jsonl` and `ARCHON_REFLECTION.jsonl` for inter-agent deliberation tracking.

2. **Dedicated Curator Logging**:
   - Modify `infra/docker/docker-compose.yml` to mount `./logs/curator:/app/logs:Z,U` for the `curation_worker` service.
   - Update `app/XNAi_rag_app/workers/library_curator.py` to ensure logs are written to `/app/logs/curator.log`.

3. **Heartbeat Logger**:
   - Implement `app/XNAi_rag_app/core/xnai_heartbeat.py` to log system vitals and agent status every 15 minutes to `.logs/heartbeat.jsonl`.

### Phase 2: IAM Gate Fix (Refined)
1. **Refactor `app/XNAi_rag_app/services/database.py`**:
   - Change `DATABASE_URL` to default to `postgresql://postgres:${POSTGRES_PASSWORD}@xnai_postgres:5432/xnai` when running in a container.
   - Use `lru_cache` for the engine to ensure it only initializes once with hydrated environment variables.

### Phase 3: Marathon Analytics & Study
1. **Create `scripts/marathon_analytics.py`**:
   - Develop a tool that aggregates data from `.logs/sessions/`, `.logs/heartbeat.jsonl`, and `ARCHON_REFLECTION.jsonl`.
   - Output a structured "Marathon Post-Mortem" report including wall-time, token estimates, and council deliberation highlights.

## Verification & Testing
1. **Verify Logging**: Ensure `logs/curator/curator.log` is created and populated on worker start.
2. **Verify IAM Fix**: Restart `xnai_library_curator` via Podman and check for clean initialization.
3. **Verify Heartbeat**: Monitor `.logs/heartbeat.jsonl` for entries.
4. **YOLO-Check**: Execute `podman logs xnai_library_curator` directly once in Implementation Mode to verify real-time state.

## Integration & Roadmap
- This unblocks **Phase 4 (Hellenic Ingestion)**.
- Future AMRs will run "Headless" to avoid the React UI state crash.
